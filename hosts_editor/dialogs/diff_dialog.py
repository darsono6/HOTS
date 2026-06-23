"""
Diff preview dialog shown before saving the hosts file.
To change the diff viewer appearance, edit this file.
"""

import difflib
import tkinter as tk
from tkinter import ttk

from ..constants import DARK
from ..widgets import make_btn, DarkToplevel
from ..i18n import T


class DiffDialog(DarkToplevel):
    """Shows the differences between the current file and the new version before saving."""

    def __init__(self, parent, old_text: str, new_text: str, on_confirm):
        super().__init__(parent, title=T("diff_title"), body_bg=DARK["bg"],
                          resizable=True, min_width=860, min_height=500)
        self.on_confirm = on_confirm

        hdr = tk.Frame(self.body, bg=DARK["bg2"],
                       highlightthickness=1, highlightbackground=DARK["border"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=T("diff_header"), bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=14, pady=8)
        for color, key in ((DARK["diff_add_fg"], "diff_added"),
                           (DARK["diff_del_fg"], "diff_removed")):
            tk.Label(hdr, text=T(key), bg=DARK["bg2"], fg=color,
                     font=("Segoe UI", 9)).pack(side="left")

        txt_frame = tk.Frame(self.body, bg=DARK["bg"])
        txt_frame.pack(fill="both", expand=True, padx=8, pady=(6, 0))

        self.text = tk.Text(
            txt_frame,
            bg=DARK["bg2"], fg=DARK["fg"],
            font=("Cascadia Code", 9),
            relief="flat", bd=0,
            state="disabled",
            wrap="none",
            selectbackground=DARK["sel_bg"],
            insertbackground=DARK["fg"],
        )

        # ── SCROLLBAR STYLING AND CREATION (SWITCHED TO TTK) ─────────────
        hsb_style = ttk.Style()
        hsb_style.configure("Dark.Horizontal.TScrollbar",
                             background=DARK["bg3"], 
                             troughcolor=DARK["bg"],
                             bordercolor=DARK["bg"], 
                             arrowcolor=DARK["fg2"])
        hsb_style.map("Dark.Horizontal.TScrollbar",
                       background=[("active", DARK["accent"]), ("pressed", DARK["accent"])])

        xsb = ttk.Scrollbar(txt_frame, orient="horizontal",
                            style="Dark.Horizontal.TScrollbar", command=self.text.xview)
        ysb = ttk.Scrollbar(txt_frame, orient="vertical",
                            command=self.text.yview)
        # ─────────────────────────────────────────────────────────────────

        self.text.configure(xscrollcommand=xsb.set, yscrollcommand=ysb.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")
        txt_frame.rowconfigure(0, weight=1)
        txt_frame.columnconfigure(0, weight=1)

        self.text.tag_configure("add", foreground=DARK["diff_add_fg"],
                                background=DARK["diff_add"])
        self.text.tag_configure("del", foreground=DARK["diff_del_fg"],
                                background=DARK["diff_del"])
        self.text.tag_configure("hdr", foreground="#888888",
                                background=DARK["bg3"])
        self.text.tag_configure("ctx", foreground=DARK["fg2"])

        self._fill_diff(old_text, new_text)

        adds = sum(1 for l in self._diff_lines if l.startswith("+") and not l.startswith("+++"))
        dels = sum(1 for l in self._diff_lines if l.startswith("-") and not l.startswith("---"))
        stat_txt = T("diff_no_changes") if adds + dels == 0 else T("diff_stat", adds=adds, dels=dels)
        tk.Label(hdr, text=stat_txt, bg=DARK["bg2"], fg=DARK["fg2"],
                 font=("Segoe UI", 9)).pack(side="left", padx=16)

        save_label = T("diff_save_anyway") if adds + dels == 0 else T("diff_save")
        make_btn(hdr, "💾", "#60c8ff", save_label,
                 self._confirm, accent=True).pack(side="right", padx=6, pady=4)
        make_btn(hdr, "✖", "#e05050", T("diff_cancel"),
                 self.destroy).pack(side="right", padx=3, pady=4)

        self.center_on_parent(min_w=860, min_h=500)

    def _fill_diff(self, old: str, new: str):
        old_lines = old.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)
        self._diff_lines = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile=T("diff_fromfile"), tofile=T("diff_tofile"),
            lineterm=""))

        self.text.configure(state="normal")
        self.text.delete("1.0", "end")

        if not self._diff_lines:
            self.text.insert("end", T("diff_no_changes_body"), "ctx")
        else:
            for line in self._diff_lines:
                s = line.rstrip("\n")
                if s.startswith("+++") or s.startswith("---") or s.startswith("@@"):
                    tag = "hdr"
                elif s.startswith("+"):
                    tag = "add"
                elif s.startswith("-"):
                    tag = "del"
                else:
                    tag = "ctx"
                self.text.insert("end", s + "\n", tag)

        self.text.configure(state="disabled")

    def _confirm(self):
        self.destroy()
        self.on_confirm()