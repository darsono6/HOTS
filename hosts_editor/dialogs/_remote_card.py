"""Options page: "Remote administration" panel (connect this PC to a HOTS web console)."""

import os
import sys
import time

from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget, QGridLayout
from PySide6.QtCore import QThread, Signal

from ..constants import DARK
from ..icons import FIF
from ..i18n import T
from ..bg_tasks import register_qthread
from ..widgets_qt import HOTSButton, HOTSDialog


def _line_field(placeholder: str = "") -> QLineEdit:
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    e.setStyleSheet(
        f"QLineEdit {{ background-color: {DARK['indicator_bg']}; color: {DARK['fg']}; "
        f"border: 1px solid {DARK['border']}; border-radius: 4px; padding: 5px 8px; }}"
        f"QLineEdit:focus {{ border: 1px solid {DARK['accent']}; background-color: {DARK['panel_bg_strong']}; }}"
    )
    return e


def _label(text: str, size: str = "9pt", color: str = None) -> QLabel:
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(f"color: {color or DARK['fg']}; font-size: {size}; background: transparent; border: none;")
    return lbl


def _launcher_script() -> str:
    main = sys.modules.get("__main__")
    return os.path.abspath(getattr(main, "__file__", "") or sys.argv[0])


class _RemoteWorker(QThread):
    done = Signal(bool, str)

    def __init__(self, mode: str, server: str = "", code: str = "", parent=None):
        super().__init__(parent)
        self._mode, self._server, self._code = mode, server, code

    def run(self):
        from ..remote import service
        try:
            if self._mode == "connect":
                code, message = service.connect(self._server, self._code, _launcher_script())
                self.done.emit(code == service.EXIT_OK, message)
            else:
                service.disconnect(notify_server=True)
                self.done.emit(True, "")
        except Exception as e:  # never crash the GUI
            self.done.emit(False, str(e))


class RemotePanel(QWidget):
    """Expandable panel content. `on_state_changed(title)` updates the card title."""

    def __init__(self, on_state_changed=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._on_state_changed = on_state_changed
        self._worker = None

        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 14)
        v.setSpacing(8)

        self._status = _label("", "9pt")
        v.addWidget(self._status)

        self._form = QWidget()
        grid = QGridLayout(self._form)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(4)
        self._server = _line_field("https://console.example.com")
        self._code = _line_field("ABCD-EFGH")
        grid.addWidget(_label(T("remote_lbl_server")), 0, 0)
        grid.addWidget(_label(T("remote_lbl_code")), 0, 1)
        grid.addWidget(self._server, 1, 0)
        grid.addWidget(self._code, 1, 1)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 1)
        v.addWidget(self._form)

        row = QHBoxLayout()
        row.setSpacing(8)
        self._err = _label("", "8pt", "#ff6060")
        row.addWidget(self._err, 1)
        self._connect_btn = HOTSButton(FIF.CONNECT, "#ffffff", T("remote_btn_connect"), accent=True)
        self._connect_btn.fit_to_content(min_width=110)
        self._connect_btn.clicked.connect(self._connect)
        row.addWidget(self._connect_btn)
        self._disconnect_btn = HOTSButton(FIF.DELETE, DARK["red"], T("remote_btn_disconnect"))
        self._disconnect_btn.fit_to_content(min_width=110)
        self._disconnect_btn.clicked.connect(self._disconnect)
        row.addWidget(self._disconnect_btn)
        v.addLayout(row)

        self._code.returnPressed.connect(self._connect)
        self.refresh()

    # -- state ---------------------------------------------------------------------------------
    def card_title(self) -> str:
        from ..remote import config
        return T("opt_remote_on") if config.is_enrolled() else T("opt_remote")

    def refresh(self):
        from ..remote import config
        cfg = config.load()
        status = config.read_status()
        if cfg:
            text = T("remote_status_on", url=cfg.get("server_url", ""))
            if status.get("connected") is True:
                text += "\n" + T("remote_state_connected")
            elif status.get("last_error"):
                text += "\n" + T("remote_state_offline", err=status.get("last_error", "")[:200])
            elif status.get("updated_at") and time.time() - status["updated_at"] > 120:
                text += "\n" + T("remote_state_offline", err="?")
        else:
            text = T("remote_status_off")
        self._status.setText(text)
        self._form.setVisible(cfg is None)
        self._connect_btn.setVisible(cfg is None)
        self._disconnect_btn.setVisible(cfg is not None)
        self._err.setText("")
        if self._on_state_changed:
            self._on_state_changed(self.card_title())

    def _busy(self, busy: bool):
        self._connect_btn.setEnabled(not busy)
        self._disconnect_btn.setEnabled(not busy)

    def _start(self, worker: _RemoteWorker):
        self._worker = worker
        register_qthread(worker)
        worker.done.connect(self._on_done)
        self._busy(True)
        worker.start()

    # -- actions -------------------------------------------------------------------------------
    def _connect(self):
        server, code = self._server.text().strip(), self._code.text().strip()
        if not server or not code:
            self._err.setText(T("remote_err_fields"))
            return
        self._err.setText(T("remote_connecting"))
        self._start(_RemoteWorker("connect", server, code, self))

    def _disconnect(self):
        if not HOTSDialog.ask(self, T("opt_remote"), T("remote_disconnect_confirm")):
            return
        self._start(_RemoteWorker("disconnect", parent=self))

    def _on_done(self, ok: bool, message: str):
        mode = self._worker._mode if self._worker else ""
        self._worker = None
        self._busy(False)
        if mode == "connect":
            if ok:
                self._code.clear()
                self.refresh()
                HOTSDialog.info(self, T("opt_remote"), T("remote_ok_msg", url=self._server.text().strip()))
            else:
                self._err.setText(T("remote_fail_msg", err=message))
        else:
            self.refresh()
            if not ok:
                HOTSDialog.error(self, T("opt_remote"), message)
