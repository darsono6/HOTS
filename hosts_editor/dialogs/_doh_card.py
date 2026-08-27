import threading
import time

import shiboken6

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget, QFrame,
)
from PySide6.QtCore import Qt, QObject, Signal, QTimer
from PySide6.QtGui import QColor

from qfluentwidgets import FluentIcon as FIF, IconWidget

from ..constants import DARK
from ..core_doh import BROWSERS, DohBlockManager
from ..widgets_qt import HOTSButton, HOTSDialog, attach_fluent_tip, colored_svg_icon
from ..i18n import T
from ..bg_tasks import start_bg_thread, is_shutting_down
from ._parental_shared import _InfoButton


class _DohToggleSignals(QObject):
    done = Signal(bool, object)


class _DohRow(QWidget):

    def __init__(self, browser: dict, installed: bool, blocked: bool, on_toggle, parent=None):
        super().__init__(parent)
        self._browser_id = browser["id"]
        self._on_toggle = on_toggle
        self._blocked = blocked

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
        toggle_color = DARK["green"] if blocked else DARK["fg2"]
        toggle_btn.setIcon(colored_svg_icon(toggle_icon, QColor(toggle_color), sizes=(22,)))
        _hover_rules = (
            "QToolButton:hover { background: rgba(128, 128, 128, 30); }"
            "QToolButton:pressed { background: rgba(128, 128, 128, 45); }"
        )
        if blocked:
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
        toggle_btn.setEnabled(installed)
        if installed:
            tip_text = T("doh_row_toggle_off_tooltip") if blocked else T("doh_row_toggle_on_tooltip")
        else:
            tip_text = T("doh_row_toggle_not_installed_tooltip")
        attach_fluent_tip(toggle_btn, tip_text)
        toggle_btn.clicked.connect(lambda: self._on_toggle(self._browser_id, not self._blocked))
        h.addWidget(toggle_btn, 0, Qt.AlignVCenter)

        ico = IconWidget(FIF.GLOBE)
        ico.setFixedSize(14, 14)
        h.addWidget(ico, 0, Qt.AlignVCenter)

        lbl = QLabel(browser["name"])
        lbl.setStyleSheet(f"color: {DARK['fg']}; font-size: 9pt; background: transparent; border: none;")
        h.addWidget(lbl, 1)

        if installed:
            status_text = T("doh_row_status_blocked") if blocked else T("doh_row_status_unblocked")
            status_color = DARK["green"] if blocked else DARK["fg2"]
        else:
            status_text = T("doh_row_status_not_installed")
            status_color = DARK["fg2"]
        status = QLabel(status_text)
        status.setStyleSheet(f"color: {status_color}; font-size: 8pt; background: transparent; border: none;")
        h.addWidget(status, 0, Qt.AlignVCenter)

        self.setStyleSheet(f"background: {DARK['bg3']}; border-radius: 4px;")


class _DohBlockCardMixin:

    def _make_doh_card(self, header_height: int = 64) -> QWidget:
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

        doh_icon = FIF.CERTIFICATE if hasattr(FIF, "CERTIFICATE") else FIF.GLOBE
        icon = IconWidget(doh_icon)
        icon.setFixedSize(20, 20)
        icon.setIcon(colored_svg_icon(doh_icon, QColor(DARK["accent"]), sizes=(20,)))
        h.addWidget(icon, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        title = QLabel(T("doh_title"))
        title.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent; border: none;")
        title_row.addWidget(title)
        title_row.addWidget(_InfoButton(T("doh_tooltip")))
        title_row.addStretch()
        text_col.addLayout(title_row)

        desc = QLabel(T("doh_desc"))
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
        self._doh_header = header

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

        list_container = QVBoxLayout()
        list_container.setSpacing(4)
        v.addLayout(list_container)

        section_state = {"expanded": getattr(self, "_doh_section_expanded", False)}

        def _apply_section_state(expanded: bool):
            body.setVisible(expanded)
            sep.setVisible(expanded)
            attach_fluent_tip(toggle_btn, T("par_categories_collapse") if expanded else T("par_categories_expand"))
            toggle_btn.set_icon(chevron_open if expanded else chevron_closed, DARK["fg2"], glyph_color=DARK["accent"])
            toggle_btn.set_accent(False)

        def _toggle_section():
            expanded = not section_state["expanded"]
            section_state["expanded"] = expanded
            self._doh_section_expanded = expanded
            _apply_section_state(expanded)

        toggle_btn.clicked.connect(_toggle_section)
        _apply_section_state(section_state["expanded"])

        state = {
            "outer": outer, "list_container": list_container,
            "busy": False,
        }
        self._doh_state = state

        self._doh_refresh_list(state)
        return outer

    def _doh_set_busy(self, state: dict, busy: bool):
        was_busy = state["busy"]
        state["busy"] = busy
        container = state["list_container"]
        for i in range(container.count()):
            w = container.itemAt(i).widget()
            if w is not None:
                w.setEnabled(not busy)
        if busy and not was_busy:
            self.begin_busy()
        elif not busy and was_busy:
            self.end_busy()

    def _doh_refresh_list(self, state: dict):
        container = state["list_container"]
        while container.count():
            item = container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for browser in BROWSERS:
            installed = DohBlockManager.is_browser_installed(browser["id"])
            blocked = DohBlockManager.is_blocked(browser["id"]) if installed else False
            row = _DohRow(
                browser, installed, blocked,
                on_toggle=lambda bid, new_val, s=state: self._doh_toggle(s, bid, new_val),
            )
            container.addWidget(row)

    _DOH_MIN_BUSY_MS = 450

    def _doh_toggle(self, state: dict, browser_id: str, new_blocked: bool):
        if state["busy"]:
            return
        self._doh_set_busy(state, True)
        state["busy_started_at"] = time.monotonic()
        signals = _DohToggleSignals(self)
        signals.done.connect(lambda ok, extra: self._doh_on_toggle_done(state, ok, extra))
        self._doh_signals = signals

        def worker():
            ok = False
            err = None
            try:
                ok = DohBlockManager.enable(browser_id) if new_blocked else DohBlockManager.disable(browser_id)
                if not ok:
                    err = DohBlockManager.last_error
            except Exception as e:
                err = str(e)
            signals.done.emit(ok, err)

        start_bg_thread(worker)

    def _doh_on_toggle_done(self, state: dict, ok: bool, err):
        if not shiboken6.isValid(self) or is_shutting_down():
            return
        elapsed_ms = (time.monotonic() - state.get("busy_started_at", time.monotonic())) * 1000
        remaining_ms = max(0, int(self._DOH_MIN_BUSY_MS - elapsed_ms))
        QTimer.singleShot(remaining_ms, lambda: self._doh_finish_toggle(state, ok, err))

    def _doh_finish_toggle(self, state: dict, ok: bool, err):
        if not shiboken6.isValid(self) or is_shutting_down():
            return
        self._doh_set_busy(state, False)
        if ok:
            self._doh_refresh_list(state)
        else:
            if err == "no_admin":
                msg = T("doh_err_no_admin")
            else:
                msg = T("doh_err_generic")
                if err:
                    msg += f"\n\n{err}"
            HOTSDialog.error(self, T("doh_title"), msg)
