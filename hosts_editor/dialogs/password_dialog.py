import hashlib

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget
from PySide6.QtCore import Qt

from qfluentwidgets import FluentIcon as FIF

from ..constants import DARK
from ..widgets_qt import HOTSDialog, HOTSButton, h_separator, attach_line_edit_context_menu
from ..i18n import T


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


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


class SetPasswordDialog(HOTSDialog):
    def __init__(self, parent, current_hash: str, on_save):
        super().__init__(parent, T("pwd_set_title"), min_width=360, min_height=280)
        self._on_save  = on_save
        self._cur_hash = current_hash
        self._has_pass = bool(current_hash)
        self._build()
        self.adjustSize()
        self.center_on_parent()

    def _build(self):
        cl = self.body_layout
        cl.setContentsMargins(22, 16, 22, 12)
        cl.setSpacing(8)

        info_color = "#d4800a" if self._has_pass else DARK["fg2"]
        info_text  = T("pwd_info_on") if self._has_pass else T("pwd_info_off")
        info = QLabel(info_text)
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {info_color}; background: transparent;")
        cl.addWidget(info)

        self._old_edit = None
        if self._has_pass:
            cl.addWidget(self._flbl(T("pwd_lbl_current")))
            self._old_edit = _pass_field()
            cl.addWidget(self._old_edit)

        cl.addWidget(self._flbl(T("pwd_lbl_new")))
        self._new_edit = _pass_field()
        cl.addWidget(self._new_edit)

        cl.addWidget(self._flbl(T("pwd_lbl_repeat")))
        self._rep_edit = _pass_field()
        cl.addWidget(self._rep_edit)
        self._rep_edit.returnPressed.connect(self._confirm)

        self._err = QLabel("")
        self._err.setStyleSheet(f"color: #ff6060; font-size: 8pt; background: transparent;")
        cl.addWidget(self._err)
        cl.addWidget(h_separator())

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = HOTSButton(FIF.SAVE, "#ffffff", T("pwd_btn_set"), accent=True)
        save_btn.fit_to_content()
        save_btn.clicked.connect(self._confirm)
        btn_row.addWidget(save_btn)

        if self._has_pass:
            del_btn = HOTSButton(FIF.DELETE, DARK["red"], T("pwd_btn_remove"))
            del_btn.fit_to_content()
            del_btn.clicked.connect(self._remove_password)
            btn_row.addWidget(del_btn)

        cancel_btn = HOTSButton(FIF.CLOSE, DARK["red"], T("pwd_btn_cancel"))
        cancel_btn.fit_to_content()
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)

    def _flbl(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(f"color: {DARK['fg']}; font-size: 9pt; background: transparent;")
        return l

    def _set_err(self, msg: str):
        self._err.setText(msg)

    def _confirm(self):
        if self._old_edit is not None:
            old_val = self._old_edit.text()
            if not old_val:
                self._set_err(T("pwd_err_no_current"))
                return
            if _hash(old_val) != self._cur_hash:
                self._set_err(T("pwd_err_wrong"))
                self._old_edit.clear()
                self._old_edit.setFocus()
                return

        new_val = self._new_edit.text()
        rep_val = self._rep_edit.text()
        if not new_val:
            self._set_err(T("pwd_err_empty"))
            return
        if len(new_val) < 4:
            self._set_err(T("pwd_err_too_short"))
            return
        if new_val != rep_val:
            self._set_err(T("pwd_err_mismatch"))
            self._rep_edit.clear()
            self._rep_edit.setFocus()
            return

        self._on_save(_hash(new_val))
        self.accept()
        HOTSDialog.info(self.parent(), T("pwd_set_ok_title"), T("pwd_set_ok_msg"))

    def _remove_password(self):
        if self._old_edit is not None:
            old_val = self._old_edit.text()
            if not old_val:
                self._set_err(T("pwd_err_no_for_remove"))
                return
            if _hash(old_val) != self._cur_hash:
                self._set_err(T("pwd_err_wrong"))
                self._old_edit.clear()
                self._old_edit.setFocus()
                return
        self._on_save("")
        self.accept()
        HOTSDialog.info(self.parent(), T("pwd_remove_ok_title"), T("pwd_remove_ok_msg"))


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
        self._err.setStyleSheet(f"color: #ff6060; font-size: 8pt; background: transparent;")
        cl.addWidget(self._err)
        cl.addWidget(h_separator())

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = HOTSButton(FIF.ACCEPT, "#ffffff", T("pwd_btn_confirm"), accent=True)
        ok_btn.fit_to_content()
        ok_btn.clicked.connect(self._confirm)
        btn_row.addWidget(ok_btn)

        cancel_btn = HOTSButton(FIF.CLOSE, DARK["red"], T("pwd_btn_cancel"))
        cancel_btn.fit_to_content()
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
        if hashlib.sha256(val.encode()).hexdigest() != self._cur_hash:
            self._err.setText(T("pwd_err_wrong_retry"))
            self._entry.clear()
            self._entry.setFocus()
            return
        
        super().accept()
        self._on_success()
