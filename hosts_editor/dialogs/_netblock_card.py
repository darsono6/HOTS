import shiboken6

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QColor

from ..icons import FIF
from ..ui_parts import IconWidget
from ..constants import DARK
from ..core_netblock import NetBlockManager
from ..widgets_qt import HOTSButton, HOTSDialog, attach_fluent_tip, colored_svg_icon
from ..i18n import T
from ..bg_tasks import start_bg_thread, is_shutting_down
from ._parental_shared import _InfoButton


class _NetBlockToggleSignals(QObject):
    done = Signal(bool)


def _status_style(color: str) -> str:
    return f"color: {color}; font-size: 8.5pt; background: transparent; border: none;"


class _NetBlockCardMixin:

    def _make_netblock_card(self) -> QWidget:
        active = NetBlockManager.is_active()
        outer = QWidget()
        outer.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 8px;"
        )
        h = QHBoxLayout(outer)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(10)

        icon = IconWidget(FIF.GLOBE)
        icon.setFixedSize(20, 20)
        icon.setIcon(colored_svg_icon(FIF.GLOBE, QColor(DARK["accent"]), sizes=(20,)))
        h.addWidget(icon, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        title = QLabel(T("netblock_title"))
        title.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent; border: none;")
        title_row.addWidget(title)
        title_row.addWidget(_InfoButton(T("netblock_tooltip")))
        title_row.addStretch()
        text_col.addLayout(title_row)

        desc = QLabel(T("netblock_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        text_col.addWidget(desc)

        status_lbl = QLabel(T("netblock_status_blocked") if active else T("netblock_status_open"))
        status_lbl.setStyleSheet(_status_style(DARK["green"] if active else DARK["fg2"]))
        text_col.addWidget(status_lbl)
        h.addLayout(text_col, 1)

        side_col = QVBoxLayout()
        side_col.setSpacing(4)
        side_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        btn = HOTSButton(FIF.ACCEPT if active else FIF.CLOSE, DARK["green"] if active else DARK["gray"], "", accent=False)
        btn.setFixedWidth(44)
        attach_fluent_tip(btn, T("netblock_btn_disable") if active else T("netblock_btn_enable"))
        side_col.addWidget(btn, 0, Qt.AlignRight)
        h.addLayout(side_col)

        state = {"active": active, "btn": btn, "status_lbl": status_lbl, "busy": False}
        self._netblock_state = state
        self._netblock_card_widget = outer
        btn.clicked.connect(lambda _c=False, s=state: self._toggle_netblock(s))
        return outer

    def _toggle_netblock(self, state: dict):
        if state["busy"]:
            return
        target = not state["active"]
        if target and not HOTSDialog.ask(self, T("netblock_title"), T("netblock_confirm")):
            return
        state["busy"] = True
        state["btn"].setEnabled(False)
        self.begin_busy()

        signals = _NetBlockToggleSignals(self)
        signals.done.connect(lambda ok, s=state, t=target: self._on_netblock_toggle_done(s, t, ok))
        self._netblock_signals = signals

        def worker(t=target):
            try:
                ok = NetBlockManager.enable() if t else NetBlockManager.disable()
            except Exception as e:
                ok = False
                NetBlockManager.last_error = str(e)
            signals.done.emit(ok)

        start_bg_thread(worker)

    def _on_netblock_toggle_done(self, state: dict, target: bool, ok: bool):
        if not shiboken6.isValid(self) or is_shutting_down():
            return
        state["busy"] = False
        state["btn"].setEnabled(True)
        self.end_busy()

        if ok:
            state["active"] = target
            self._refresh_netblock_card(state)
            HOTSDialog.info(self, T("netblock_title"), T("netblock_on_ok" if target else "netblock_off_ok"))
        else:
            self._refresh_netblock_card(state)
            err_msg = T("netblock_on_fail" if target else "netblock_off_fail")
            if NetBlockManager.last_error:
                err_msg += f"\n\n{NetBlockManager.last_error}"
            HOTSDialog.error(self, T("netblock_title"), err_msg)

    def _refresh_netblock_card(self, state: dict):
        active = state["active"]
        btn = state["btn"]
        attach_fluent_tip(btn, T("netblock_btn_disable") if active else T("netblock_btn_enable"))
        btn.set_icon(FIF.ACCEPT if active else FIF.CLOSE, DARK["green"] if active else DARK["gray"])
        btn.set_accent(False)

        status_lbl = state["status_lbl"]
        status_lbl.setText(T("netblock_status_blocked") if active else T("netblock_status_open"))
        status_lbl.setStyleSheet(_status_style(DARK["green"] if active else DARK["fg2"]))

    def apply_netblock_drift_result(self, result):
        if not shiboken6.isValid(self) or is_shutting_down():
            return
        state = getattr(self, "_netblock_state", None)
        if not state or result is None:
            return
        state["active"] = NetBlockManager.is_active()
        self._refresh_netblock_card(state)
        status_lbl = state["status_lbl"]
        if result == "regressed":
            status_lbl.setText(T("netblock_drift_regressed"))
            status_lbl.setStyleSheet(_status_style(DARK["red"]))
        elif result == "restored":
            status_lbl.setText(T("netblock_drift_restored"))
            status_lbl.setStyleSheet(_status_style(DARK["green"]))
