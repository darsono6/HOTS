"""
Backup manager dialog for the hosts file.
To change the backup window UI, edit this file.
"""

import shutil
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk

from ..constants import DARK
from ..core import list_backups, flush_dns_cache
from ..widgets import make_btn, DarkDialog, DarkToplevel
from ..i18n import T


class BackupManagerDialog(DarkToplevel):
    def __init__(self, parent, hosts_path, on_restore):
        super().__init__(parent, title=T("bak_title"), body_bg=DARK["bg"],
                          resizable=True, min_width=720, min_height=420)
        self.hosts_path = hosts_path
        self.on_restore = on_restore

        # ── Header (icon + description) — same style as the diagnostics dialogs
        hdr = tk.Frame(self.body, bg=DARK["bg2"],
                       highlightthickness=1, highlightbackground=DARK["border"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="\U0001f4be", bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI Emoji", 18)).pack(side="left", padx=(12, 6), pady=8)

        desc_col = tk.Frame(hdr, bg=DARK["bg2"])
        desc_col.pack(side="left", padx=4, pady=8)
        tk.Label(desc_col, text=T("bak_header"),
                 bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI", 10, "bold"), justify="left").pack(anchor="w")
        tk.Label(desc_col, text=T("bak_subheader"),
                 bg=DARK["bg2"], fg=DARK["fg2"],
                 font=("Segoe UI", 9), justify="left").pack(anchor="w")

        # ── Table ────────────────────────────────────────────────────────
        tbl_frame = tk.Frame(self.body, bg=DARK["bg"])
        tbl_frame.pack(fill="both", expand=True, padx=8, pady=6)

        cols = ("date", "size", "path")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                 selectmode="extended", style="Backup.Treeview")
        self.tree.heading("date", text=T("bak_col_date"))
        self.tree.heading("size", text=T("bak_col_size"))
        self.tree.heading("path", text=T("bak_col_file"))
        self.tree.column("date", width=160, stretch=False)
        self.tree.column("size", width=80,  stretch=False, anchor="e")
        self.tree.column("path", width=380)

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

        # ── Status bar (very bottom) + action bar (just above it) ──────────
        # Packed in this order on purpose: each new side="bottom" widget
        # docks above the previous one, so status ends up at the true
        # bottom edge and the action bar sits just above it — same
        # stacking diagnostics_dialog.py uses.
        self._status = tk.Label(self.body, text="", anchor="w", padx=10, pady=3,
                                bg=DARK["bg2"], fg=DARK["fg2"], font=("Segoe UI", 9),
                                highlightthickness=1, highlightbackground=DARK["border"])
        self._status.pack(fill="x", side="bottom")

        act_bar = tk.Frame(self.body, bg=DARK["bg2"],
                           highlightthickness=1, highlightbackground=DARK["border"])
        act_bar.pack(fill="x", side="bottom")
        make_btn(act_bar, "♻", "#4ec94e", T("bak_btn_restore"),
                 self._restore, accent=True).pack(side="left", padx=(6, 3), pady=5)
        make_btn(act_bar, "🗑", "#e05050", T("bak_btn_delete"),
                 self._delete_bak).pack(side="left", padx=3, pady=5)
        tk.Label(act_bar, text=T("bak_hint_multi"),
                 bg=DARK["bg2"], fg=DARK["fg2"],
                 font=("Segoe UI", 8)).pack(side="right", padx=10)

        self._refresh()
        self.center_on_parent(min_w=720, min_h=420)

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        self._baks = list_backups(self.hosts_path)
        if not self._baks:
            self.tree.insert("", "end", values=(T("bak_empty"), "", ""))
        else:
            for p, dt in self._baks:
                size = p.stat().st_size
                size_str = f"{size/1024:.1f} KB" if size >= 1024 else f"{size} B"
                self.tree.insert("", "end", iid=str(p),
                                 values=(dt.strftime("%Y-%m-%d  %H:%M:%S"), size_str, str(p)))
        self._status.configure(text=T("bak_status_count", n=len(self._baks)))

    def _selected_paths(self):
        sel = self.tree.selection()
        if not sel:
            DarkDialog.info(self, T("no_sel_title"), T("bak_no_sel_msg"))
            return []
        return [Path(s) for s in sel]

    def _restore(self):
        paths = self._selected_paths()
        if not paths:
            return
        if len(paths) > 1:
            DarkDialog.info(self, T("bak_too_many_title"), T("bak_too_many_msg"))
            return
        p = paths[0]
        if not DarkDialog.ask(self, T("bak_restore_ask_title"),
                              T("bak_restore_ask_msg", name=p.name)):
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(self.hosts_path, self.hosts_path + f".bak_{ts}")
        shutil.copy2(str(p), self.hosts_path)
        flush_dns_cache()
        DarkDialog.info(self, T("save_success_title"), T("bak_restore_ok"))
        self._refresh()
        self._status.configure(text=T("bak_status_restored", name=p.name))
        self.on_restore()

    def _delete_bak(self):
        paths = self._selected_paths()
        if not paths:
            return
        names = "\n".join(p.name for p in paths)
        if len(paths) > 1:
            q = T("bak_del_ask_many", n=len(paths), names=names)
        else:
            q = T("bak_del_ask_one", name=paths[0].name)
        if not DarkDialog.ask(self, T("bak_del_ask_title"), q):
            return
        n = len(paths)
        for p in paths:
            p.unlink(missing_ok=True)
        self._refresh()
        self._status.configure(text=T("bak_status_deleted", n=n))
