from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit
from PySide6.QtCore import QTimer

from ..icons import FIF
from ..constants import DARK
from ..widgets_qt import HOTSDialog, HOTSButton, h_separator, attach_line_edit_context_menu
from ..i18n import T
from ..password_utils import verify_password


def _pass_field(placeholder="") -> QLineEdit:
    e = QLineEdit()
    e.setEchoMode(QLineEdit.Password)
    e.setPlaceholderText(placeholder)
    e.setStyleSheet(
        f"QLineEdit {{ background-color: {DARK['indicator_bg']}; color: {DARK['fg']}; "
        f"border: 1px solid {DARK['border']}; border-radius: 4px; padding: 5px 8px; }}"
        f"QLineEdit:focus {{ border: 1px solid {DARK['accent']}; background-color: {DARK['panel_bg_strong']}; }}"
    )
    attach_line_edit_context_menu(e)
    return e


class PasswordPromptDialog(HOTSDialog):
    def __init__(self, parent, current_hash: str, on_success, on_cancel=None):
        import sys
        super().__init__(parent, T("pwd_prompt_title"), min_width=340, min_height=220)
        self._cur_hash   = current_hash
        self._on_success = on_success
        self._cancel_cb  = on_cancel or (lambda: sys.exit(0))
        self._build()
        self.adjustSize()
        self.center_on_parent()

    def reject(self):
        self._cancel_cb()
        super().reject()

    def _build(self):
        cl = self.body_layout
        cl.setContentsMargins(22, 16, 22, 12)
        cl.setSpacing(8)

        intro = QLabel(T("pwd_prompt_intro"))
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {DARK['fg2']}; background: transparent;")
        cl.addWidget(intro)

        lbl = QLabel(T("pwd_lbl_password"))
        lbl.setStyleSheet(f"color: {DARK['fg']}; font-size: 9pt; background: transparent;")
        cl.addWidget(lbl)
        
        self._entry = _pass_field()
        self._entry.returnPressed.connect(self._confirm)
        cl.addWidget(self._entry)

        self._err = QLabel("")
        self._err.setStyleSheet("color: #ff6060; font-size: 8pt; background: transparent;")
        cl.addWidget(self._err)
        cl.addWidget(h_separator())

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = HOTSButton(FIF.ACCEPT, "#ffffff", T("pwd_btn_confirm"), accent=True)
        ok_btn.fit_to_content(min_width=100)
        ok_btn.clicked.connect(self._confirm)
        btn_row.addWidget(ok_btn)

        cancel_btn = HOTSButton(FIF.CLOSE, DARK["red"], T("pwd_btn_cancel"))
        cancel_btn.fit_to_content(min_width=100)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)

        self._entry.setFocus()

    def _confirm(self):
        val = self._entry.text()
        if not val:
            self._err.setText(T("pwd_err_empty_field"))
            return
        if not verify_password(val, self._cur_hash):
            self._err.setText(T("pwd_err_wrong_retry"))
            self._entry.clear()
            self._entry.setFocus()
            return
        
        super().accept()
        QTimer.singleShot(0, self._on_success)
