"""
HOTS password management dialogs.

SetPasswordDialog    — set / change / remove the password
PasswordPromptDialog — verify the password at application startup
"""

import hashlib
import tkinter as tk

from ..constants import DARK
from ..widgets   import DarkDialog, DarkToplevel, make_btn
from ..i18n      import T


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _make_pass_entry(parent) -> tk.Entry:
    return tk.Entry(
        parent,
        show="●",
        bg=DARK["bg3"],
        fg=DARK["fg"],
        insertbackground=DARK["fg"],
        selectbackground=DARK["accent"],
        selectforeground=DARK["accent_fg"],
        relief="flat",
        bd=0,
        font=("Segoe UI", 10),
        highlightthickness=1,
        highlightbackground=DARK["border"],
        highlightcolor=DARK["accent"],
    )


class _BasePassDialog(DarkToplevel):
    def __init__(self, parent, title: str):
        super().__init__(parent, title=title, body_bg=DARK["bg"], padx=22, pady=18)
        self._body = self.body  # kept for compatibility with existing _build_body() code

    def _close(self):
        # Routes the titlebar ✕ through the same hook subclasses already use
        self._on_cancel()

    def _on_cancel(self):
        self.destroy()

    def _center(self, parent):
        # Kept for backward compatibility — delegates to the shared helper
        self.center_on_parent()


class SetPasswordDialog(_BasePassDialog):
    def __init__(self, parent, current_hash: str, on_save):
        super().__init__(parent, T("pwd_set_title"))
        self._on_save  = on_save
        self._cur_hash = current_hash
        self._has_pass = bool(current_hash)
        self._build_body()
        self._center(parent)

    def _build_body(self):
        body = self._body

        if self._has_pass:
            info       = T("pwd_info_on")
            info_color = "#80ffb0"
        else:
            info       = T("pwd_info_off")
            info_color = DARK["fg2"]

        tk.Label(body, text=info, bg=DARK["bg"], fg=info_color,
                 font=("Segoe UI", 9), justify="left", anchor="w").pack(fill="x", pady=(0, 14))

        if self._has_pass:
            tk.Label(body, text=T("pwd_lbl_current"), bg=DARK["bg"], fg=DARK["fg"],
                     font=("Segoe UI", 9)).pack(anchor="w")
            self._old_entry = _make_pass_entry(body)
            self._old_entry.pack(fill="x", pady=(2, 10), ipady=5)
            self._old_entry.bind("<Return>", lambda _: self._new_entry.focus_set())
        else:
            self._old_entry = None

        tk.Label(body, text=T("pwd_lbl_new"), bg=DARK["bg"], fg=DARK["fg"],
                 font=("Segoe UI", 9)).pack(anchor="w")
        self._new_entry = _make_pass_entry(body)
        self._new_entry.pack(fill="x", pady=(2, 6), ipady=5)
        self._new_entry.bind("<Return>", lambda _: self._rep_entry.focus_set())

        tk.Label(body, text=T("pwd_lbl_repeat"), bg=DARK["bg"], fg=DARK["fg"],
                 font=("Segoe UI", 9)).pack(anchor="w")
        self._rep_entry = _make_pass_entry(body)
        self._rep_entry.pack(fill="x", pady=(2, 4), ipady=5)
        self._rep_entry.bind("<Return>", lambda _: self._confirm())

        self._err_lbl = tk.Label(body, text="", bg=DARK["bg"], fg="#ff6060",
                                  font=("Segoe UI", 8))
        self._err_lbl.pack(anchor="w", pady=(2, 10))

        btn_row = tk.Frame(body, bg=DARK["bg"])
        btn_row.pack(fill="x", pady=(4, 0))
        make_btn(btn_row, "✔", "#4ec94e", T("pwd_btn_set"),    self._confirm).pack(side="left", padx=(0, 6))
        if self._has_pass:
            make_btn(btn_row, "🗑", "#e05050", T("pwd_btn_remove"), self._remove_password).pack(side="left", padx=(0, 6))
        make_btn(btn_row, "✕", "#a0a0a0", T("pwd_btn_cancel"), self.destroy).pack(side="left")

        (self._old_entry if self._old_entry else self._new_entry).focus_set()

    def _err(self, msg: str):
        self._err_lbl.config(text=msg)

    def _confirm(self):
        if self._old_entry is not None:
            old_val = self._old_entry.get()
            if not old_val:
                self._err(T("pwd_err_no_current"))
                return
            if _hash(old_val) != self._cur_hash:
                self._err(T("pwd_err_wrong"))
                self._old_entry.delete(0, "end")
                self._old_entry.focus_set()
                return

        new_val = self._new_entry.get()
        rep_val = self._rep_entry.get()

        if not new_val:
            self._err(T("pwd_err_empty"))
            return
        if len(new_val) < 4:
            self._err(T("pwd_err_too_short"))
            return
        if new_val != rep_val:
            self._err(T("pwd_err_mismatch"))
            self._rep_entry.delete(0, "end")
            self._rep_entry.focus_set()
            return

        self._on_save(_hash(new_val))
        self.destroy()
        DarkDialog.info(self.master, T("pwd_set_ok_title"), T("pwd_set_ok_msg"))

    def _remove_password(self):
        if self._old_entry is not None:
            old_val = self._old_entry.get()
            if not old_val:
                self._err(T("pwd_err_no_for_remove"))
                return
            if _hash(old_val) != self._cur_hash:
                self._err(T("pwd_err_wrong"))
                self._old_entry.delete(0, "end")
                self._old_entry.focus_set()
                return
        self._on_save("")
        self.destroy()
        DarkDialog.info(self.master, T("pwd_remove_ok_title"), T("pwd_remove_ok_msg"))


class PasswordPromptDialog(_BasePassDialog):
    def __init__(self, parent, current_hash: str, on_success, on_cancel=None):
        import sys
        super().__init__(parent, T("pwd_prompt_title"))
        self._cur_hash   = current_hash
        self._on_success = on_success
        self._cancel_cb  = on_cancel or (lambda: sys.exit(0))
        self._build_body()
        self._center(parent)

    def _on_cancel(self):
        self.destroy()
        self._cancel_cb()

    def _build_body(self):
        body = self._body

        tk.Label(body, text=T("pwd_prompt_intro"),
                 bg=DARK["bg"], fg=DARK["fg2"],
                 font=("Segoe UI", 9), justify="left").pack(anchor="w", pady=(0, 14))

        tk.Label(body, text=T("pwd_lbl_password"), bg=DARK["bg"], fg=DARK["fg"],
                 font=("Segoe UI", 9)).pack(anchor="w")
        self._entry = _make_pass_entry(body)
        self._entry.pack(fill="x", pady=(2, 4), ipady=5)
        self._entry.bind("<Return>", lambda _: self._confirm())

        self._err_lbl = tk.Label(body, text="", bg=DARK["bg"], fg="#ff6060",
                                  font=("Segoe UI", 8))
        self._err_lbl.pack(anchor="w", pady=(2, 10))

        btn_row = tk.Frame(body, bg=DARK["bg"])
        btn_row.pack(fill="x")
        make_btn(btn_row, "✔", "#4ec94e", T("pwd_btn_confirm"), self._confirm).pack(side="left", padx=(0, 6))
        make_btn(btn_row, "✕", "#a0a0a0", T("pwd_btn_cancel"),  self._on_cancel).pack(side="left")

        self._entry.focus_set()

    def _confirm(self):
        val = self._entry.get()
        if not val:
            self._err_lbl.config(text=T("pwd_err_empty_field"))
            return
        if _hash(val) != self._cur_hash:
            self._err_lbl.config(text=T("pwd_err_wrong_retry"))
            self._entry.delete(0, "end")
            self._entry.focus_set()
            return
        self.destroy()
        self._on_success()
