import threading

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget, QScrollArea, QCheckBox, QPushButton,
)
from PySide6.QtCore import Qt, QSize, QObject, Signal
from PySide6.QtGui import QColor

from qfluentwidgets import FluentIcon as FIF, IconWidget
try:
    from qfluentwidgets import IndeterminateProgressRing
except ImportError:
    IndeterminateProgressRing = None

from ..constants import DARK
from ..widgets_qt import HOTSPage, HOTSDialog, HOTSButton, h_separator
from ..i18n import T
from ..core_antispy import AntiSpyManager, ITEMS
from ..core_restore import SystemRestoreManager

from ._parental_shared import (
    _blocklists_dir, _AntiSpySignals, _ParentalCardMixin,
)

def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w:
            w.deleteLater()
        else:
            child_layout = item.layout()
            if child_layout:
                _clear_layout(child_layout)

def _items_for_level(level: str) -> list:
    return [it for it in ITEMS if it["level"] == level]

_LABEL_KEY_BY_ID = {it["id"]: it["label_key"] for it in ITEMS}

def _level_any_active(level: str) -> bool:
    return any(AntiSpyManager.get_items_status(level).values())

def _level_counts(level: str) -> tuple:
    items_status = AntiSpyManager.get_items_status(level)
    available_ids = [iid for iid in items_status if not AntiSpyManager.is_item_missing(iid)]
    items_total = len(available_ids)
    items_active = sum(1 for iid in available_ids if items_status[iid])
    return items_active, items_total

class _ChecklistSignals(QObject):
    done = Signal(bool, list)

class _RestorePointSignals(QObject):
    done = Signal(str, str)

class _RemoveLimitSignals(QObject):
    done = Signal(bool, str)


class PrivacyPage(_ParentalCardMixin, HOTSPage):
    busy_changed = Signal(bool)

    def __init__(self, parent=None):
        import re as _re_title
        clean_title = _re_title.sub(r"[^\w\s/.:,!?()-]", "", T("priv_title")).strip()
        super().__init__("privacyInterface", FIF.HIDE, clean_title, parent)
        self._bdir = _blocklists_dir()
        self._states = {}
        self._antispy_states = {}
        self._antispy_busy = set()
        self._antispy_signals = {}
        self._checklist_states = {}
        self._drifted_ids = set()
        self._bg_signal_objs: list = []
        self._watchdog_running = False
        self._manual_ops_active = 0
        self._pending_refresh = False
        self._parent_win = parent
        self._build()

    def refresh_content(self):
        if self._manual_ops_active > 0:
            self._pending_refresh = True
            return
        self._pending_refresh = False
        self._states = {}
        self._antispy_states = {}
        self._antispy_busy = set()
        self._antispy_signals = {}
        self._checklist_states = {}
        _clear_layout(self.content_layout)
        self._build()

    def _update_watchdog_indicator(self):
        spinner = getattr(self, "_watchdog_spinner", None)
        lbl = getattr(self, "_watchdog_status_lbl", None)
        if lbl is None:
            return
        busy = self._watchdog_running or self._manual_ops_active > 0
        if busy:
            if spinner is not None:
                spinner.setVisible(True)
            lbl.setText(T("priv_watchdog_checking") if self._watchdog_running
                        else T("priv_op_working"))
        else:
            if spinner is not None:
                spinner.setVisible(False)
            lbl.setText("")

    def _mark_op_start(self):
        was_idle = self._manual_ops_active == 0
        self._manual_ops_active += 1
        self._update_watchdog_indicator()
        if was_idle:
            self.busy_changed.emit(True)

    def _mark_op_end(self):
        self._manual_ops_active = max(0, self._manual_ops_active - 1)
        self._update_watchdog_indicator()
        if self._manual_ops_active == 0:
            self.busy_changed.emit(False)

    def disconnect_bg_signals(self):
        for sig in self._bg_signal_objs:
            try:
                sig.done.disconnect()
            except Exception:
                pass
        self._bg_signal_objs.clear()

    def set_drifted(self, drifted_ids):
        self._drifted_ids = set(drifted_ids)
        self._watchdog_running = False
        if self._manual_ops_active > 0:
            self._pending_refresh = True
            self._update_watchdog_indicator()
            return
        self.refresh_content()

    def set_watchdog_running(self, running: bool):
        self._watchdog_running = running
        self._update_watchdog_indicator()

    def _level_effective_active(self, level: str) -> bool:
        return _level_any_active(level)

    def _build(self):
        rl = self.content_layout

        sub_row = QHBoxLayout()
        sub = QLabel(T("priv_subheader"))
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent;")
        sub_row.addWidget(sub, 1)

        self._watchdog_spinner = None
        if IndeterminateProgressRing is not None:
            self._watchdog_spinner = IndeterminateProgressRing()
            self._watchdog_spinner.setFixedSize(14, 14)
            self._watchdog_spinner.setStrokeWidth(2)
            sub_row.addWidget(self._watchdog_spinner, 0, Qt.AlignTop)
            sub_row.addSpacing(6)

        self._watchdog_status_lbl = QLabel("")
        self._watchdog_status_lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent;")
        sub_row.addWidget(self._watchdog_status_lbl, 0, Qt.AlignTop)

        rl.addLayout(sub_row)
        rl.addSpacing(10)
        rl.addWidget(h_separator())

        self._update_watchdog_indicator()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(12, 10, 12, 10)
        inner_lay.setSpacing(6)

        inner_lay.addWidget(self._make_antispy_section())
        inner_lay.addStretch()
        scroll.setWidget(inner)
        rl.addWidget(scroll, 1)

    def _make_restore_banner(self) -> QWidget:
        outer = QWidget()
        outer.setStyleSheet(
            f"background: {DARK['bg3']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        h = QHBoxLayout(outer)
        h.setContentsMargins(12, 10, 12, 10)
        h.setSpacing(12)

        icon = IconWidget(FIF.HISTORY)
        icon.setFixedSize(20, 20)
        h.addWidget(icon, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        title = QLabel(T("priv_restore_banner_title"))
        title.setStyleSheet(f"color: {DARK['fg']}; font-size: 9.5pt; font-weight: 600; background: transparent; border: none;")
        text_col.addWidget(title)
        desc = QLabel(T("priv_restore_banner_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8.5pt; background: transparent; border: none;")
        text_col.addWidget(desc)
        result_lbl = QLabel("")
        result_lbl.setWordWrap(True)
        result_lbl.setVisible(False)
        result_lbl.setStyleSheet(f"color: {DARK['green']}; font-size: 8.5pt; background: transparent; border: none;")
        text_col.addWidget(result_lbl)

        accent = DARK["accent"]

        remove_row = QHBoxLayout()
        remove_row.setContentsMargins(0, 0, 0, 0)
        remove_row.setSpacing(4)
        remove_hint_lbl = QLabel(T("priv_restore_remove_limit_hint"))
        remove_hint_lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        remove_row.addWidget(remove_hint_lbl)
        remove_link_lbl = QLabel(T("priv_restore_remove_limit_link"))
        remove_link_lbl.setStyleSheet(
            f"color: {accent}; font-size: 8pt; font-weight: 600; text-decoration: underline; "
            "background: transparent; border: none;"
        )
        remove_link_lbl.setCursor(Qt.PointingHandCursor)
        remove_link_lbl.setToolTip(T("priv_restore_remove_limit_tooltip"))
        remove_row.addWidget(remove_link_lbl)
        remove_row.addStretch(1)
        remove_widget = QWidget()
        remove_widget.setStyleSheet("background: transparent; border: none;")
        remove_widget.setLayout(remove_row)
        remove_widget.setVisible(False)
        text_col.addWidget(remove_widget)

        h.addLayout(text_col, 1)

        create_btn = HOTSButton(FIF.SAVE, accent, T("priv_restore_btn_create"))
        create_btn.fit_to_content()
        h.addWidget(create_btn, 0, Qt.AlignTop)

        state = {
            "btn": create_btn, "result_lbl": result_lbl, "busy": False,
            "remove_widget": remove_widget, "remove_hint_lbl": remove_hint_lbl,
            "remove_link_lbl": remove_link_lbl, "remove_busy": False,
        }
        create_btn.clicked.connect(lambda _c=False, s=state: self._create_restore_point(s))
        remove_link_lbl.mousePressEvent = lambda _e, s=state: self._remove_restore_limit(s)
        return outer

    def _create_restore_point(self, state: dict):
        if state["busy"]:
            return
        state["busy"] = True
        self._mark_op_start()
        btn = state["btn"]
        btn.setEnabled(False)
        btn.set_label(T("priv_restore_btn_working"))
        btn.fit_to_content()
        state["result_lbl"].setVisible(False)
        state["remove_widget"].setVisible(False)

        signals = _RestorePointSignals()
        signals.done.connect(lambda status, details, s=state: self._on_restore_point_done(s, status, details))
        self._restore_signals = signals
        self._bg_signal_objs.append(signals)

        import threading

        def worker():
            try:
                status, details = SystemRestoreManager.create_restore_point(T("priv_restore_point_description"))
            except Exception as e:
                status, details = "error", str(e)
            signals.done.emit(status, details)

        threading.Thread(target=worker, daemon=True).start()

    def _on_restore_point_done(self, state: dict, status: str, details: str):
        state["busy"] = False
        btn = state["btn"]
        btn.setEnabled(True)
        btn.set_label(T("priv_restore_btn_create"))
        btn.fit_to_content()

        lbl = state["result_lbl"]
        if status == "created":
            lbl.setText(T("priv_restore_msg_created"))
            lbl.setStyleSheet(f"color: {DARK['green']}; font-size: 8.5pt; background: transparent; border: none;")
        elif status == "throttled":
            lbl.setText(T("priv_restore_msg_throttled"))
            lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8.5pt; background: transparent; border: none;")
            state["remove_widget"].setVisible(True)
        elif status == "no_admin":
            lbl.setText(T("priv_restore_msg_no_admin"))
            lbl.setStyleSheet(f"color: {DARK['red']}; font-size: 8.5pt; background: transparent; border: none;")
        else:
            lbl.setText(T("priv_restore_msg_error", details=details or "?"))
            lbl.setStyleSheet(f"color: {DARK['red']}; font-size: 8.5pt; background: transparent; border: none;")
        lbl.setVisible(True)
        self._mark_op_end()

    def _remove_restore_limit(self, state: dict):
        if state["busy"] or state["remove_busy"]:
            return
        state["remove_busy"] = True
        self._mark_op_start()

        link_lbl = state["remove_link_lbl"]
        link_lbl.setText(T("priv_restore_remove_limit_working"))
        link_lbl.setCursor(Qt.ArrowCursor)

        signals = _RemoveLimitSignals()
        signals.done.connect(lambda ok, details, s=state: self._on_remove_limit_done(s, ok, details))
        self._remove_limit_signals = signals
        self._bg_signal_objs.append(signals)

        def worker():
            try:
                ok, details = SystemRestoreManager.remove_frequency_limit()
            except Exception as e:
                ok, details = False, str(e)
            signals.done.emit(ok, details)

        threading.Thread(target=worker, daemon=True).start()

    def _on_remove_limit_done(self, state: dict, ok: bool, details: str):
        state["remove_busy"] = False

        link_lbl = state["remove_link_lbl"]
        lbl = state["result_lbl"]
        if ok:
            state["remove_widget"].setVisible(False)
            lbl.setText(T("priv_restore_limit_removed"))
            lbl.setStyleSheet(f"color: {DARK['green']}; font-size: 8.5pt; background: transparent; border: none;")
            lbl.setVisible(True)
        else:
            link_lbl.setText(T("priv_restore_remove_limit_link"))
            link_lbl.setCursor(Qt.PointingHandCursor)
            lbl.setText(T("priv_restore_limit_remove_error", details=details or "?"))
            lbl.setStyleSheet(f"color: {DARK['red']}; font-size: 8.5pt; background: transparent; border: none;")
            lbl.setVisible(True)
        self._mark_op_end()

    def _make_antispy_section(self) -> QWidget:
        outer = QWidget()
        outer.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        v = QVBoxLayout(outer)
        v.setContentsMargins(16, 14, 16, 16)
        v.setSpacing(10)

        desc = QLabel(T("par_antispy_section_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        v.addWidget(desc)

        v.addWidget(h_separator())

        v.addWidget(self._make_restore_banner())
        v.addWidget(h_separator())

        level_configs = [
            {"level": "basic", "icon": FIF.HIDE, "label_key": "par_antispy_basic_btn",
             "success_label_key": "par_antispy_basic_label",
             "enable_fn": AntiSpyManager.enable_basic, "disable_fn": AntiSpyManager.disable_basic,
             "badge_color": "#0078D4"},
            {"level": "medium", "icon": FIF.GLOBE, "label_key": "par_antispy_medium_btn",
             "success_label_key": "par_antispy_medium_label",
             "enable_fn": AntiSpyManager.enable_medium, "disable_fn": AntiSpyManager.disable_medium,
             "badge_color": "#8764B8"},
            {"level": "advanced", "icon": FIF.SETTING, "label_key": "par_antispy_advanced_btn",
             "success_label_key": "par_antispy_advanced_label",
             "enable_fn": AntiSpyManager.enable_advanced, "disable_fn": AntiSpyManager.disable_advanced,
             "badge_color": "#CA5010"},
        ]

        for cfg in level_configs:
            v.addWidget(self._make_level_card(cfg))
            v.addSpacing(6)

        v.addSpacing(2)
        v.addWidget(h_separator())
        v.addSpacing(6)

        domains_cat = {"label_key": "par_cat_antispy_domains", "icon": "📡", "color": "#0078D4", "file": "telemetry.txt"}
        v.addWidget(self._make_card(domains_cat))

        return outer

    def _make_level_card(self, cfg: dict) -> QWidget:
        level = cfg["level"]
        accent = cfg["badge_color"]

        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent; border: none;")
        wrap_lay = QVBoxLayout(wrapper)
        wrap_lay.setContentsMargins(0, 0, 0, 0)
        wrap_lay.setSpacing(4)

        card = self._card_frame(accent)
        info_lay = card.property("info_lay")
        btn_lay = card.property("btn_lay")

        title_row = QHBoxLayout()
        ico = IconWidget(cfg["icon"])
        ico.setFixedSize(16, 16)
        ico.setIcon(cfg["icon"].icon(color=QColor(accent)))
        title_row.addWidget(ico)
        t = QLabel(T(cfg["label_key"]))
        t.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent;")
        title_row.addWidget(t)
        title_row.addStretch()
        info_lay.addLayout(title_row)

        items_status = AntiSpyManager.get_items_status(level)
        active = any(items_status.values())
        items_active, items_total = _level_counts(level)
        level_ids = {it["id"] for it in _items_for_level(level)}
        drifted_here = self._drifted_ids & level_ids
        if drifted_here:
            status_txt = T("priv_level_status_drift", n=len(drifted_here))
            status_fg = DARK["red"]
        else:
            status_txt = T("priv_level_status", active=items_active, total=items_total)
            status_fg = DARK["green"] if items_active == items_total else DARK["fg2"]
        st_lbl = QLabel(status_txt)
        st_lbl.setStyleSheet(f"color: {status_fg}; font-size: 9pt; background: transparent;")
        info_lay.addWidget(st_lbl)

        gear_btn = QPushButton()
        gear_btn.setIcon(FIF.SETTING.icon(color=QColor(DARK["fg2"])))
        gear_btn.setIconSize(QSize(13, 13))
        gear_btn.setFixedSize(24, 24)
        gear_btn.setFlat(True)
        gear_btn.setCursor(Qt.PointingHandCursor)
        gear_btn.setToolTip(T("priv_gear_tooltip"))
        gear_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid transparent; border-radius: 4px; }"
            f"QPushButton:hover {{ background: {DARK['btn_hover']}; border: 1px solid {DARK['border']}; }}"
        )
        btn_lay.addWidget(gear_btn)

        btn_color = DARK["red"] if active else DARK["green"]
        btn_label = T("par_btn_disable") if active else T("par_btn_enable")
        btn_icon = FIF.CLOSE if active else FIF.ACCEPT

        btn = HOTSButton(btn_icon, btn_color, btn_label, accent=False)
        btn.fit_to_content()
        btn_lay.addWidget(btn)

        state = dict(cfg)
        state["btn"] = btn
        state["active"] = active
        state["key"] = level
        state["status_lbl"] = st_lbl
        self._antispy_states[level] = state
        btn.clicked.connect(lambda _checked=False, s=state: self._toggle_antispy_module(s))

        wrap_lay.addWidget(card)

        checklist = self._make_checklist(level, state, accent, items_status=items_status)
        gear_btn.clicked.connect(lambda _c=False, w=checklist: w.setVisible(not w.isVisible()))
        wrap_lay.addWidget(checklist)

        return wrapper

    def _make_checklist(self, level: str, module_state: dict, accent: str = None,
                         items_status: dict = None) -> QWidget:
        accent = accent or DARK["accent"]
        checklist = QWidget()
        checklist.setVisible(False)
        checklist.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        cl_lay = QVBoxLayout(checklist)
        cl_lay.setContentsMargins(8, 8, 8, 8)
        cl_lay.setSpacing(6)

        hint = QLabel(T("priv_checklist_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        cl_lay.addWidget(hint)

        if items_status is None:
            items_status = AntiSpyManager.get_items_status(level)
        checkboxes = {}
        labels = {}
        for item in _items_for_level(level):
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(12)

            is_drifted = item["id"] in self._drifted_ids
            is_missing = AntiSpyManager.is_item_missing(item["id"])
            cb_color = DARK["red"] if is_drifted else accent

            cb = QCheckBox()
            cb.setChecked(False if is_missing else items_status.get(item["id"], False))
            cb.setEnabled(not is_missing)
            cb.setFocusPolicy(Qt.NoFocus)
            cb.setFixedSize(20, 20)
            if is_missing:
                cb.setStyleSheet(
                    "QCheckBox { background: transparent; border: none; outline: none; spacing: 0px; margin: 0px; padding: 2px; }\n"
                    f"QCheckBox::indicator {{ width: 12px; height: 12px; border: 1px solid {DARK['border_faint']}; "
                    f"border-radius: 6px; background: {DARK['bg3']}; }}"
                )
                cb.setToolTip(T("priv_item_missing_tooltip"))
            else:
                cb.setStyleSheet(
                    f"QCheckBox {{ background: transparent; border: none; outline: none; spacing: 0px; margin: 0px; padding: 2px; }}\n"
                    f"QCheckBox::indicator {{ width: 12px; height: 12px; border: 1px solid {DARK['border']}; "
                    f"border-radius: 6px; background: {DARK['indicator_bg']}; }}\n"
                    f"QCheckBox::indicator:hover {{ border: 1px solid {cb_color}; }}\n"
                    f"QCheckBox::indicator:checked {{ background: transparent; border: 3px solid {cb_color}; }}"
                )
            row.addWidget(cb, 0, Qt.AlignTop)

            lbl_text = T(item["label_key"])
            if is_missing:
                lbl_text = lbl_text + "  " + T("priv_item_missing_suffix")
            elif is_drifted:
                lbl_text = "⚠ " + lbl_text
            text_col = QVBoxLayout()
            text_col.setContentsMargins(0, 0, 0, 0)
            text_col.setSpacing(1)

            lbl = QLabel(lbl_text)
            lbl.setWordWrap(True)
            lbl.setMinimumWidth(0)
            lbl_color = DARK["fg2"] if is_missing else (DARK["red"] if is_drifted else DARK["fg"])
            lbl.setStyleSheet(f"color: {lbl_color}; background: transparent; font-size: 10pt; border: none; padding-left: 2px;")
            if is_missing:
                lbl.setCursor(Qt.ArrowCursor)
                lbl.setToolTip(T("priv_item_missing_tooltip"))
            else:
                lbl.setCursor(Qt.PointingHandCursor)
                if is_drifted:
                    lbl.setToolTip(T("priv_item_drift_tooltip"))
                lbl.mousePressEvent = lambda _e, c=cb: c.setChecked(not c.isChecked())
            text_col.addWidget(lbl)

            desc_key = item.get("desc_key")
            if desc_key:
                desc_lbl = QLabel(T(desc_key))
                desc_lbl.setWordWrap(True)
                desc_lbl.setMinimumWidth(0)
                desc_fg = DARK["border"] if is_missing else DARK["fg2"]
                desc_lbl.setStyleSheet(f"color: {desc_fg}; background: transparent; font-size: 8.5pt; border: none; padding-left: 2px;")
                if is_missing:
                    desc_lbl.setCursor(Qt.ArrowCursor)
                    desc_lbl.setToolTip(T("priv_item_missing_tooltip"))
                else:
                    desc_lbl.setCursor(Qt.PointingHandCursor)
                    desc_lbl.mousePressEvent = lambda _e, c=cb: c.setChecked(not c.isChecked())
                text_col.addWidget(desc_lbl)

            row.addLayout(text_col, 1)

            cl_lay.addLayout(row)
            checkboxes[item["id"]] = cb
            labels[item["id"]] = lbl

        apply_btn = HOTSButton(FIF.SYNC, accent, T("priv_checklist_apply_btn"), accent=True)
        apply_btn.fit_to_content()
        apply_row = QHBoxLayout()
        apply_row.addStretch()
        apply_row.addWidget(apply_btn)
        apply_row.addStretch()
        cl_lay.addLayout(apply_row)

        checklist_state = {
            "level": level,
            "checkboxes": checkboxes,
            "labels": labels,
            "apply_btn": apply_btn,
            "module_state": module_state,
            "accent": accent,
        }
        self._checklist_states[level] = checklist_state
        apply_btn.clicked.connect(lambda _c=False, s=checklist_state: self._apply_checklist(s))

        return checklist

    def _apply_checklist(self, state: dict):
        level = state["level"]
        busy_key = f"checklist_{level}"
        if busy_key in self._antispy_busy:
            return
        self._antispy_busy.add(busy_key)
        self._mark_op_start()

        apply_btn = state["apply_btn"]
        apply_btn.setEnabled(False)
        apply_btn.set_label(T("par_btn_working"))
        apply_btn.fit_to_content()
        for cb in state["checkboxes"].values():
            cb.setEnabled(False)

        selected_ids = [iid for iid, cb in state["checkboxes"].items() if cb.isChecked()]

        signals = _ChecklistSignals()
        signals.done.connect(lambda ok, warnings, s=state: self._on_checklist_applied(s, ok, warnings))
        self._antispy_signals[busy_key] = signals
        self._bg_signal_objs.append(signals)

        import threading

        def worker(lvl=level, ids=selected_ids):
            try:
                ok = AntiSpyManager.apply_selected(lvl, ids)
                warnings = list(AntiSpyManager.last_warnings)
            except Exception as e:
                ok = False
                AntiSpyManager.last_error = str(e)
                warnings = []
            signals.done.emit(ok, warnings)

        threading.Thread(target=worker, daemon=True).start()

    def _on_checklist_applied(self, state: dict, ok: bool, warnings: list):
        level = state["level"]
        self._antispy_busy.discard(f"checklist_{level}")

        apply_btn = state["apply_btn"]
        apply_btn.setEnabled(True)
        apply_btn.set_label(T("priv_checklist_apply_btn"))
        apply_btn.set_icon(FIF.SYNC, state.get("accent", DARK["accent"]))
        apply_btn.set_accent(True)
        apply_btn.fit_to_content()

        self._sync_checklist_checkboxes(level)
        for iid, cb in state["checkboxes"].items():
            if not AntiSpyManager.is_item_missing(iid):
                cb.setEnabled(True)

        if ok:
            level_ids = {it["id"] for it in _items_for_level(level)}
            self._drifted_ids -= level_ids
            accent = state.get("accent", DARK["accent"])
            for iid, lbl in state.get("labels", {}).items():
                if AntiSpyManager.is_item_missing(iid):
                    continue
                lbl.setText(T(_LABEL_KEY_BY_ID[iid]))
                lbl.setStyleSheet(f"color: {DARK['fg']}; background: transparent; font-size: 10pt; border: none; padding-left: 2px;")
                lbl.setToolTip("")
            for iid, cb in state["checkboxes"].items():
                if AntiSpyManager.is_item_missing(iid):
                    continue
                cb.setStyleSheet(
                    f"QCheckBox {{ background: transparent; border: none; outline: none; spacing: 0px; margin: 0px; padding: 2px; }}\n"
                    f"QCheckBox::indicator {{ width: 12px; height: 12px; border: 1px solid {DARK['border']}; "
                    f"border-radius: 6px; background: {DARK['indicator_bg']}; }}\n"
                    f"QCheckBox::indicator:hover {{ border: 1px solid {accent}; }}\n"
                    f"QCheckBox::indicator:checked {{ background: transparent; border: 3px solid {accent}; }}"
                )

        module_state = state["module_state"]
        module_state["active"] = self._level_effective_active(level)
        self._refresh_antispy_btn(module_state)
        self._mark_op_end()

        if not ok:
            err_msg = T("par_antispy_err_msg")
            if AntiSpyManager.last_error:
                err_msg += f"\n\n{AntiSpyManager.last_error}"
            HOTSDialog.error(self, T("par_antispy_err_title"), err_msg)
        elif warnings:
            HOTSDialog.info(self, T("par_success_title"),
                            T(module_state["success_label_key"]) + "\n\n" + "\n".join(warnings))
        else:
            HOTSDialog.info(self, T("par_success_title"), T(module_state["success_label_key"]))

    def _sync_checklist_checkboxes(self, level: str):
        cl_state = self._checklist_states.get(level)
        if not cl_state:
            return
        items_status = AntiSpyManager.get_items_status(level)
        for iid, cb in cl_state["checkboxes"].items():
            cb.blockSignals(True)
            cb.setChecked(items_status.get(iid, False))
            cb.blockSignals(False)

    def _toggle_antispy_module(self, state: dict):
        key = state["key"]
        if key in self._antispy_busy:
            return
        target = not state["active"]

        self._antispy_busy.add(key)
        self._mark_op_start()
        btn = state["btn"]
        btn.setEnabled(False)
        btn.set_label(T("par_btn_working"))
        btn.fit_to_content()

        signals = _AntiSpySignals()
        signals.done.connect(lambda ok, s=state, t=target: self._on_antispy_module_done(s, t, ok))
        self._antispy_signals[key] = signals
        self._bg_signal_objs.append(signals)

        import threading

        def worker(s=state, t=target):
            try:
                fn = s["enable_fn"] if t else s["disable_fn"]
                ok = fn()
                s["_last_warnings"] = list(AntiSpyManager.last_warnings)
            except Exception as e:
                ok = False
                AntiSpyManager.last_error = str(e)
                s["_last_warnings"] = []
            signals.done.emit(ok)

        threading.Thread(target=worker, daemon=True).start()

    def _on_antispy_module_done(self, state: dict, target: bool, ok: bool):
        key = state["key"]
        self._antispy_busy.discard(key)
        btn = state["btn"]
        btn.setEnabled(True)

        if not ok:
            self._refresh_antispy_btn(state)
            self._mark_op_end()
            err_msg = T("par_antispy_err_msg")
            if AntiSpyManager.last_error:
                err_msg += f"\n\n{AntiSpyManager.last_error}"
            HOTSDialog.error(self, T("par_antispy_err_title"), err_msg)
            return

        state["active"] = target
        self._refresh_antispy_btn(state)
        self._sync_checklist_checkboxes(key)
        self._mark_op_end()
        msg_key = "par_success_on" if target else "par_success_off"
        base_msg = T(msg_key, label=T(state["success_label_key"]))
        warnings = state.get("_last_warnings") or []
        if warnings:
            HOTSDialog.info(self, T("par_success_title"), base_msg + "\n\n" + "\n".join(warnings))
        else:
            HOTSDialog.info(self, T("par_success_title"), base_msg)

    def _refresh_antispy_btn(self, state: dict):
        btn    = state["btn"]
        active = state["active"]
        color  = DARK["red"] if active else DARK["green"]
        label  = T("par_btn_disable") if active else T("par_btn_enable")
        icon   = FIF.CLOSE if active else FIF.ACCEPT

        btn.set_label(label)
        btn.set_icon(icon, color)
        btn.set_accent(False)
        btn.fit_to_content()

        st_lbl = state.get("status_lbl")
        if st_lbl is not None:
            level = state["key"]
            items_active, items_total = _level_counts(level)
            level_ids = {it["id"] for it in _items_for_level(level)}
            drifted_here = self._drifted_ids & level_ids
            if drifted_here:
                st_lbl.setText(T("priv_level_status_drift", n=len(drifted_here)))
                st_lbl.setStyleSheet(f"color: {DARK['red']}; font-size: 9pt; background: transparent;")
            else:
                st_lbl.setText(T("priv_level_status", active=items_active, total=items_total))
                st_lbl.setStyleSheet(
                    f"color: {DARK['green'] if items_active == items_total else DARK['fg2']}; "
                    f"font-size: 9pt; background: transparent;"
                )
