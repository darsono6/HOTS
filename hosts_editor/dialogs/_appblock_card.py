import os
import re

import shiboken6

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget, QLineEdit, QFileDialog,
    QGraphicsOpacityEffect, QPushButton, QFrame, QCompleter,
)
from PySide6.QtCore import Qt, QObject, Signal, QSize, QStringListModel, QEvent, QRectF
from PySide6.QtGui import QColor, QPalette, QPainterPath, QRegion

from qfluentwidgets import FluentIcon as FIF, IconWidget

from ..constants import DARK, accent_rgba
from ..core_appblock import AppBlockManager
from ..widgets_qt import HOTSButton, HOTSDialog, attach_line_edit_context_menu, attach_fluent_tip, colored_svg_icon
from ..i18n import T
from ..bg_tasks import start_bg_thread, is_shutting_down
from ._parental_shared import _InfoButton


class _AppBlockSignals(QObject):
    done = Signal(bool, object)


def _dark_line_edit(placeholder: str = "") -> QLineEdit:
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    e.setFixedHeight(30)
    e.setStyleSheet(
        f"QLineEdit {{ background-color: {DARK['bg3']}; color: {DARK['fg']}; "
        f"border: 1px solid {DARK['border']}; border-radius: 4px; padding: 4px 8px; }}"
        f"QLineEdit:focus {{ border: 1px solid {DARK['accent']}; }}"
    )
    attach_line_edit_context_menu(e)
    return e


def _parse_css_color(css_value: str) -> QColor:
    m = re.match(
        r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)",
        css_value.strip(),
    )
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        return QColor(r, g, b, round(a * 255))
    return QColor(css_value)


class _RoundedCornerMasker(QObject):

    def __init__(self, radius: int, parent=None):
        super().__init__(parent)
        self._radius = radius

    def _apply_mask(self, widget: QWidget):
        if widget.width() <= 0 or widget.height() <= 0:
            return
        path = QPainterPath()
        path.addRoundedRect(QRectF(widget.rect()), self._radius, self._radius)
        widget.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def eventFilter(self, watched, event):
        if event.type() in (QEvent.Resize, QEvent.Show):
            self._apply_mask(watched)
        return False


def _style_completer_popup(completer: QCompleter):
    popup = completer.popup()

    bg_color = _parse_css_color(DARK["popup_bg"])
    bg_color.setAlpha(255)
    fg_color = QColor(DARK["fg"])

    popup.setAttribute(Qt.WA_TranslucentBackground, False)
    popup.setAutoFillBackground(True)
    pal = popup.palette()
    pal.setColor(QPalette.Base, bg_color)
    pal.setColor(QPalette.Window, bg_color)
    pal.setColor(QPalette.Text, fg_color)
    popup.setPalette(pal)

    masker = _RoundedCornerMasker(radius=8, parent=popup)
    popup.installEventFilter(masker)
    popup._corner_masker = masker

    popup.setStyleSheet(
        "QListView {"
        f"  background-color: {bg_color.name()};"
        f"  color: {DARK['fg']};"
        f"  border: 1px solid {accent_rgba(0.40)};"
        "  border-radius: 8px;"
        "  padding: 4px;"
        "  outline: none;"
        "  font-size: 9pt;"
        "}"
        "QListView::item {"
        "  padding: 6px 8px;"
        "  border-radius: 4px;"
        "}"
        "QListView::item:selected {"
        f"  background-color: {accent_rgba(0.18)};"
        f"  color: {DARK['fg']};"
        "}"
    )


class _AppBlockRow(QWidget):

    def __init__(self, exe_name: str, display_name: str,
                 enabled: bool, on_remove, on_toggle, parent=None):
        super().__init__(parent)
        self._exe_name = exe_name
        self._on_remove = on_remove
        self._on_toggle = on_toggle
        self._enabled = enabled

        h = QHBoxLayout(self)
        h.setContentsMargins(10, 6, 10, 6)
        h.setSpacing(8)

        from qfluentwidgets import TransparentToolButton

        toggle_icon = (
            FIF.POWER_BUTTON if hasattr(FIF, "POWER_BUTTON")
            else FIF.PLAY if hasattr(FIF, "PLAY")
            else FIF.ACCEPT
        )
        toggle_btn = TransparentToolButton(toggle_icon)
        toggle_btn.setFixedSize(22, 22)
        toggle_btn.setCursor(Qt.PointingHandCursor)
        toggle_color = DARK["green"] if enabled else DARK["fg2"]
        toggle_btn.setIcon(colored_svg_icon(toggle_icon, QColor(toggle_color), sizes=(22,)))
        _hover_rules = (
            "QToolButton:hover { background: rgba(128, 128, 128, 30); }"
            "QToolButton:pressed { background: rgba(128, 128, 128, 45); }"
        )
        if enabled:
            toggle_btn.setStyleSheet(
                "QToolButton { background: transparent; border: none; border-radius: 5px; }"
                + _hover_rules
            )
        else:
            toggle_btn.setStyleSheet(
                f"QToolButton {{ background: transparent; border: 1px solid {DARK['border']}; "
                f"border-radius: 5px; }}"
                + _hover_rules
            )
        attach_fluent_tip(
            toggle_btn,
            T("appblock_row_toggle_off_tooltip") if enabled else T("appblock_row_toggle_on_tooltip"),
        )
        toggle_btn.clicked.connect(lambda: self._on_toggle(self._exe_name, not self._enabled))
        h.addWidget(toggle_btn, 0, Qt.AlignVCenter)

        ico = IconWidget(FIF.APPLICATION)
        ico.setFixedSize(14, 14)
        h.addWidget(ico, 0, Qt.AlignVCenter)

        lbl = QLabel(display_name or exe_name)
        lbl.setStyleSheet(f"color: {DARK['fg']}; font-size: 9pt; background: transparent; border: none;")
        h.addWidget(lbl, 1)

        sub = QLabel(exe_name)
        sub.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        h.addWidget(sub, 0, Qt.AlignVCenter)

        rm_btn = TransparentToolButton(FIF.DELETE)
        rm_btn.setFixedSize(22, 22)
        rm_btn.setIcon(colored_svg_icon(FIF.DELETE, QColor(DARK["red"]), sizes=(22,)))
        rm_btn.setCursor(Qt.PointingHandCursor)
        attach_fluent_tip(rm_btn, T("appblock_row_remove_tooltip"))
        rm_btn.clicked.connect(lambda: self._on_remove(self._exe_name))
        h.addWidget(rm_btn, 0, Qt.AlignVCenter)

        self.setStyleSheet(
            f"background: {DARK['bg3']}; border-radius: 4px;"
        )

        if not enabled:
            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(0.5)
            self.setGraphicsEffect(effect)


class _AppBlockCardMixin:

    def _appblock_bg_result_skip(self) -> bool:
        return (not shiboken6.isValid(self)) or is_shutting_down()

    def _make_appblock_card(self, header_height: int = 64) -> QWidget:
        outer = QWidget()
        outer.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        outer_lay = QVBoxLayout(outer)
        outer_lay.setContentsMargins(0, 0, 0, 0)
        outer_lay.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(header_height)
        header.setStyleSheet("background: transparent; border: none;")
        h = QHBoxLayout(header)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(10)

        icon = IconWidget(FIF.APPLICATION)
        icon.setFixedSize(20, 20)
        icon.setIcon(colored_svg_icon(FIF.APPLICATION, QColor(DARK["accent"]), sizes=(20,)))
        h.addWidget(icon, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        title = QLabel(T("appblock_title"))
        title.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent; border: none;")
        title_row.addWidget(title)
        title_row.addWidget(_InfoButton(T("appblock_tooltip")))
        title_row.addStretch()
        text_col.addLayout(title_row)

        desc = QLabel(T("appblock_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        text_col.addWidget(desc)

        h.addLayout(text_col, 1)

        chevron_closed = FIF.CHEVRON_RIGHT_MED if hasattr(FIF, "CHEVRON_RIGHT_MED") else FIF.RIGHT_ARROW
        chevron_open = FIF.CHEVRON_DOWN_MED if hasattr(FIF, "CHEVRON_DOWN_MED") else FIF.DOWN

        toggle_btn = HOTSButton(chevron_closed, DARK["fg2"], "", accent=False, glyph_color=DARK["accent"])
        toggle_btn.setFixedWidth(44)
        attach_fluent_tip(toggle_btn, T("par_categories_expand"))
        h.addWidget(toggle_btn, 0, Qt.AlignVCenter)

        outer_lay.addWidget(header)
        self._appblock_header = header

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {DARK['border_faint']}; border: none;")
        outer_lay.addWidget(sep)

        body = QWidget()
        body.setStyleSheet("background: transparent; border: none;")
        v = QVBoxLayout(body)
        v.setContentsMargins(16, 10, 16, 14)
        v.setSpacing(8)
        outer_lay.addWidget(body)

        add_row = QHBoxLayout()
        add_row.setSpacing(8)
        search_edit = _dark_line_edit(T("appblock_search_loading"))
        search_edit.setMinimumWidth(160)
        search_edit.setEnabled(False)

        completer = QCompleter([], search_edit)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        search_edit.setCompleter(completer)
        _style_completer_popup(completer)

        add_row.addWidget(search_edit, 1)
        add_row.addWidget(_InfoButton(T("appblock_search_hint")))

        unlock_btn = QPushButton()
        unlock_btn.setIcon(colored_svg_icon(FIF.SETTING, QColor(DARK["red"]), sizes=(13,)))
        unlock_btn.setIconSize(QSize(13, 13))
        unlock_btn.setFixedSize(24, 24)
        unlock_btn.setFlat(True)
        unlock_btn.setCursor(Qt.PointingHandCursor)
        unlock_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid transparent; border-radius: 4px; }"
            f"QPushButton:hover {{ background: {DARK['btn_hover']}; border: 1px solid {DARK['border']}; }}"
        )
        attach_fluent_tip(unlock_btn, T("appblock_tooltip_force_unlock"), width=260)
        add_row.addWidget(unlock_btn, 0, Qt.AlignVCenter)
        v.addLayout(add_row)

        browse_row = QHBoxLayout()
        browse_row.setSpacing(8)
        browse_btn = HOTSButton(FIF.FOLDER, DARK["fg2"], T("appblock_btn_browse"), accent=False,
                                 glyph_color=DARK["accent"])
        browse_btn.fit_to_content()
        browse_row.addWidget(browse_btn)
        browse_row.addStretch()

        vpn_btn = HOTSButton(FIF.VPN if hasattr(FIF, "VPN") else FIF.GLOBE,
                              DARK["accent"], T("appblock_btn_block_vpn"), accent=False)
        vpn_btn.fit_to_content()
        browse_row.addWidget(vpn_btn)
        v.addLayout(browse_row)

        list_container = QVBoxLayout()
        list_container.setSpacing(4)
        v.addLayout(list_container)

        section_state = {"expanded": getattr(self, "_appblock_section_expanded", False)}

        def _apply_section_state(expanded: bool):
            body.setVisible(expanded)
            sep.setVisible(expanded)
            attach_fluent_tip(toggle_btn, T("par_categories_collapse") if expanded else T("par_categories_expand"))
            toggle_btn.set_icon(chevron_open if expanded else chevron_closed, DARK["fg2"], glyph_color=DARK["accent"])
            toggle_btn.set_accent(False)

        def _toggle_section():
            expanded = not section_state["expanded"]
            section_state["expanded"] = expanded
            self._appblock_section_expanded = expanded
            _apply_section_state(expanded)

        toggle_btn.clicked.connect(_toggle_section)
        _apply_section_state(section_state["expanded"])

        state = {
            "outer": outer, "search_edit": search_edit, "completer": completer,
            "installed_map": {},
            "vpn_btn": vpn_btn, "vpn_icon": FIF.VPN if hasattr(FIF, "VPN") else FIF.GLOBE,
            "browse_btn": browse_btn, "unlock_btn": unlock_btn,
            "list_container": list_container, "busy": False,
        }
        self._appblock_state = state

        completer.activated[str].connect(lambda text: self._appblock_search_pick(state, text))
        vpn_btn.clicked.connect(lambda: self._appblock_toggle_vpn_bundle(state))
        browse_btn.clicked.connect(lambda: self._appblock_browse_and_add(state))
        unlock_btn.clicked.connect(lambda: self._appblock_browse_and_force_unlock(state))

        self._appblock_refresh_vpn_btn(state)
        self._appblock_refresh_list(state)
        self._appblock_load_installed_async(state)
        return outer

    def _appblock_set_busy(self, state: dict, busy: bool):
        was_busy = state["busy"]
        state["busy"] = busy
        state["vpn_btn"].setEnabled(not busy)
        state["browse_btn"].setEnabled(not busy)
        state["unlock_btn"].setEnabled(not busy)
        state["search_edit"].setEnabled(not busy and bool(state.get("installed_map")))
        if busy and not was_busy:
            self.begin_busy()
        elif not busy and was_busy:
            self.end_busy()

    def _appblock_section_header(self, text: str, top_margin: int = 0) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {DARK['fg2']}; font-size: 7.5pt; font-weight: 600; "
            f"letter-spacing: 0.5px; background: transparent; border: none; "
            f"margin-top: {top_margin}px; padding-bottom: 2px;"
        )
        return lbl

    def _appblock_refresh_list(self, state: dict):
        container = state["list_container"]
        while container.count():
            item = container.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
                w.deleteLater()

        apps = AppBlockManager.list_blocked()
        if not apps:
            empty = QLabel(T("appblock_empty"))
            empty.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8.5pt; background: transparent; border: none;")
            container.addWidget(empty)
            return

        custom_apps = [a for a in apps if a.category != "vpn"]
        vpn_apps = [a for a in apps if a.category == "vpn"]

        def add_rows(section_apps):
            for app in section_apps:
                row = _AppBlockRow(app.exe_name, app.display_name, app.enabled,
                                    on_remove=lambda exe, s=state: self._appblock_remove(s, exe),
                                    on_toggle=lambda exe, val, s=state: self._appblock_toggle(s, exe, val))
                container.addWidget(row)

        show_headers = bool(custom_apps) and bool(vpn_apps)

        if custom_apps:
            if show_headers:
                container.addWidget(self._appblock_section_header(T("appblock_section_custom")))
            add_rows(custom_apps)

        if vpn_apps:
            if show_headers:
                container.addWidget(self._appblock_section_header(T("appblock_section_vpn"), top_margin=10))
            add_rows(vpn_apps)

    def _appblock_refresh_vpn_btn(self, state: dict):
        blocked = AppBlockManager.is_vpn_bundle_blocked()
        state["vpn_bundle_blocked"] = blocked
        btn = state["vpn_btn"]
        if blocked:
            btn.set_label(T("appblock_btn_unblock_vpn"))
            btn.set_icon(state["vpn_icon"], color=DARK["green"])
        else:
            btn.set_label(T("appblock_btn_block_vpn"))
            btn.set_icon(state["vpn_icon"], color=DARK["red"])
        btn.fit_to_content()

    def _appblock_start_add(self, state: dict, exe_name: str, display_name: str, file_path: str = ""):
        if state["busy"]:
            return
        self._appblock_set_busy(state, True)
        signals = _AppBlockSignals(self)
        signals.done.connect(lambda ok, extra: self._appblock_on_add_done(state, ok, extra))
        self._appblock_signals = signals

        def worker():
            ok = False
            err = None
            try:
                ok = AppBlockManager.add_app(exe_name, display_name, file_path=file_path)
                if not ok:
                    err = AppBlockManager.last_error
            except Exception as e:
                err = str(e)
            signals.done.emit(ok, err)

        start_bg_thread(worker)

    def _appblock_on_add_done(self, state: dict, ok: bool, err):
        if self._appblock_bg_result_skip():
            return
        self._appblock_set_busy(state, False)
        if ok:
            state["search_edit"].clear()
            self._appblock_refresh_list(state)
            self._appblock_refresh_vpn_btn(state)
        else:
            if err == "no_admin":
                msg = T("appblock_err_no_admin")
            elif err == "protected_system_app":
                msg = T("appblock_err_protected")
            elif err == "self_block":
                msg = T("appblock_err_self")
            else:
                msg = T("appblock_err_generic")
                if err:
                    msg += f"\n\n{err}"
            HOTSDialog.error(self, T("appblock_title"), msg)

    def _appblock_search_pick(self, state: dict, display_text: str):
        entry = state.get("installed_map", {}).get(display_text.strip().lower())
        if not entry:
            return
        display_name, path = entry
        exe_name = os.path.basename(path)
        self._appblock_start_add(state, exe_name, display_name, path)

    def _appblock_load_installed_async(self, state: dict):
        cached = getattr(self, "_appblock_installed_cache", None)
        if cached is not None:
            self._appblock_on_installed_loaded(state, cached)
            return

        signals = _AppBlockSignals(self)

        def _on_done(ok, programs):
            if not self._appblock_bg_result_skip():
                self._appblock_installed_cache = programs
            self._appblock_on_installed_loaded(state, programs)

        signals.done.connect(_on_done)
        self._appblock_load_signals = signals

        def worker():
            try:
                programs = AppBlockManager.list_installed_programs()
            except Exception:
                programs = []
            signals.done.emit(True, programs)

        start_bg_thread(worker)

    def _appblock_on_installed_loaded(self, state: dict, programs: list):
        if self._appblock_bg_result_skip():
            return
        state["installed_map"] = {name.lower(): (name, path) for name, path in programs}
        state["completer"].setModel(QStringListModel([name for name, _ in programs], state["completer"]))
        state["search_edit"].setPlaceholderText(T("appblock_search_placeholder"))
        if not state["busy"]:
            state["search_edit"].setEnabled(True)

    def _appblock_browse_and_add(self, state: dict):
        if state["busy"]:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, T("appblock_btn_browse"), "", "Programy (*.exe)"
        )
        if not path:
            return
        path = os.path.normpath(path)
        exe_name = os.path.basename(path)
        display_name = os.path.splitext(exe_name)[0]
        self._appblock_start_add(state, exe_name, display_name, path)

    def _appblock_browse_and_force_unlock(self, state: dict):
        if state["busy"]:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, T("appblock_btn_force_unlock"), "", "Programy (*.exe)"
        )
        if not path:
            return
        path = os.path.normpath(path)

        self._appblock_set_busy(state, True)
        signals = _AppBlockSignals(self)
        signals.done.connect(lambda ok, extra: self._appblock_on_force_unlock_done(state, ok, extra))
        self._appblock_signals = signals

        def worker():
            ok = False
            err = None
            try:
                ok = AppBlockManager.force_unlock(path)
                if not ok:
                    err = AppBlockManager.last_error
            except Exception as e:
                err = str(e)
            signals.done.emit(ok, (path, err))

        start_bg_thread(worker)

    def _appblock_on_force_unlock_done(self, state: dict, ok: bool, extra):
        if self._appblock_bg_result_skip():
            return
        self._appblock_set_busy(state, False)
        path, err = extra if extra else ("", None)
        if ok:
            self._appblock_refresh_list(state)
            self._appblock_refresh_vpn_btn(state)
            HOTSDialog.info(self, T("appblock_title"), T("appblock_force_unlock_ok", path=path))
        else:
            if err == "no_admin":
                msg = T("appblock_err_no_admin")
            else:
                msg = T("appblock_err_generic")
                if err:
                    msg += f"\n\n{err}"
            HOTSDialog.error(self, T("appblock_title"), msg)

    def _appblock_toggle_vpn_bundle(self, state: dict):
        if state["busy"]:
            return
        if state.get("vpn_bundle_blocked"):
            self._appblock_remove_vpn_bundle(state)
        else:
            self._appblock_add_vpn_bundle(state)

    def _appblock_add_vpn_bundle(self, state: dict):
        if state["busy"]:
            return
        self._appblock_set_busy(state, True)
        signals = _AppBlockSignals(self)
        signals.done.connect(lambda ok, extra: self._appblock_on_vpn_bundle_done(state, ok, extra))
        self._appblock_signals = signals

        def worker():
            ok_count, failed = 0, []
            try:
                ok_count, failed = AppBlockManager.add_vpn_bundle()
            except Exception:
                pass
            signals.done.emit(ok_count > 0, (ok_count, failed))

        start_bg_thread(worker)

    def _appblock_on_vpn_bundle_done(self, state: dict, ok: bool, extra):
        if self._appblock_bg_result_skip():
            return
        self._appblock_set_busy(state, False)
        self._appblock_refresh_list(state)
        self._appblock_refresh_vpn_btn(state)
        ok_count, failed = extra if extra else (0, [])
        if ok_count:
            msg = T("appblock_vpn_bundle_ok", n=ok_count)
            if failed:
                msg += "\n" + T("appblock_vpn_bundle_partial", failed=", ".join(failed))
            HOTSDialog.info(self, T("appblock_title"), msg)
        else:
            HOTSDialog.error(self, T("appblock_title"), T("appblock_err_no_admin"))

    def _appblock_remove_vpn_bundle(self, state: dict):
        if state["busy"]:
            return
        self._appblock_set_busy(state, True)
        signals = _AppBlockSignals(self)
        signals.done.connect(lambda ok, extra: self._appblock_on_vpn_bundle_removed_done(state, ok, extra))
        self._appblock_signals = signals

        def worker():
            ok_count, failed = 0, []
            try:
                ok_count, failed = AppBlockManager.remove_vpn_bundle()
            except Exception:
                pass
            signals.done.emit(ok_count > 0, (ok_count, failed))

        start_bg_thread(worker)

    def _appblock_on_vpn_bundle_removed_done(self, state: dict, ok: bool, extra):
        if self._appblock_bg_result_skip():
            return
        self._appblock_set_busy(state, False)
        self._appblock_refresh_list(state)
        self._appblock_refresh_vpn_btn(state)
        ok_count, failed = extra if extra else (0, [])
        if ok_count:
            msg = T("appblock_vpn_bundle_removed_ok", n=ok_count)
            if failed:
                msg += "\n" + T("appblock_vpn_bundle_partial", failed=", ".join(failed))
            HOTSDialog.info(self, T("appblock_title"), msg)
        else:
            HOTSDialog.error(self, T("appblock_title"), T("appblock_err_no_admin"))

    def _appblock_toggle(self, state: dict, exe_name: str, new_enabled: bool):
        if state["busy"]:
            return
        self._appblock_set_busy(state, True)
        signals = _AppBlockSignals(self)
        signals.done.connect(lambda ok, extra: self._appblock_on_toggle_done(state, ok, extra))
        self._appblock_signals = signals

        def worker():
            ok = False
            err = None
            try:
                ok = AppBlockManager.set_enabled(exe_name, new_enabled)
                if not ok:
                    err = AppBlockManager.last_error
            except Exception as e:
                err = str(e)
            signals.done.emit(ok, err)

        start_bg_thread(worker)

    def _appblock_on_toggle_done(self, state: dict, ok: bool, err):
        if self._appblock_bg_result_skip():
            return
        self._appblock_set_busy(state, False)
        if ok:
            self._appblock_refresh_list(state)
            self._appblock_refresh_vpn_btn(state)
        else:
            if err == "no_admin":
                msg = T("appblock_err_no_admin")
            else:
                msg = T("appblock_err_generic")
                if err:
                    msg += f"\n\n{err}"
            HOTSDialog.error(self, T("appblock_title"), msg)

    def _appblock_remove(self, state: dict, exe_name: str):
        if state["busy"]:
            return
        self._appblock_set_busy(state, True)
        signals = _AppBlockSignals(self)
        signals.done.connect(lambda ok, extra: self._appblock_on_remove_done(state, ok, extra))
        self._appblock_signals = signals

        def worker():
            ok = False
            err = None
            try:
                ok = AppBlockManager.remove_app(exe_name)
                if not ok:
                    err = AppBlockManager.last_error
            except Exception as e:
                err = str(e)
            signals.done.emit(ok, err)

        start_bg_thread(worker)

    def _appblock_on_remove_done(self, state: dict, ok: bool, err):
        if self._appblock_bg_result_skip():
            return
        self._appblock_set_busy(state, False)
        if ok:
            self._appblock_refresh_list(state)
            self._appblock_refresh_vpn_btn(state)
        else:
            if err == "no_admin":
                msg = T("appblock_err_no_admin")
            else:
                msg = T("appblock_err_generic")
                if err:
                    msg += f"\n\n{err}"
            HOTSDialog.error(self, T("appblock_title"), msg)
