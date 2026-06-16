"""
Main application window: toolbar, entry table, search bar.
To add a new toolbar button or change the window layout, edit this file.
"""

import os
import sys
import re
import copy
import threading
import tkinter as tk
from tkinter import ttk

from .constants import DARK, HOSTS_PATH, load_settings, save_settings
from .i18n      import T, set_lang, current_lang, LANGUAGES
from .core      import (parse_hosts, save_hosts, entries_to_text,
                         list_backups, import_hosts_file, export_hosts,
                         is_valid_ip)
from .widgets   import apply_dark_style, make_btn, _add_paste_menu, DarkDialog, CustomTitlebar
from .dialogs   import (EntryDialog, DiffDialog,
                         BackupManagerDialog, DiagnosticsDialog, ParentalDialog,
                         SupportDialog, SetPasswordDialog, PasswordPromptDialog)


class HostsEditor(tk.Tk):
    def __init__(self):
        super().__init__()

        # ── Custom titlebar (hides the system title bar) ──────────────────
        self.overrideredirect(True)
        self.configure(bg=DARK["bg"])
        apply_dark_style(self)

        # Override hover behavior for all scrollbars (accent color instead of white)
        style = ttk.Style()
        style.map("TScrollbar",
                  background=[("active", DARK["accent"]), ("pressed", DARK["accent"])],
                  thumb=[("active", DARK["accent"]), ("pressed", DARK["accent"])])

        self.entries   = []
        self._settings = load_settings()

        # ── UI language ─────────────────────────────────────────────────────
        set_lang(self._settings.get("language", "en"))

        # Fit geometry to screen — guard against off-screen placement
        self._saved_geo = self._settings.get("geometry", "")
        self.geometry(self._safe_geometry(self._saved_geo))
        self.minsize(660, 420)
        self._resize_start = None

        # ── Logo loading (supports PyInstaller .exe and relative paths) ────
        self._logo_img = None
        
        logo_path = self._settings.get("logo_path", "")
        
        if not logo_path or not os.path.exists(logo_path):
            if hasattr(sys, '_MEIPASS'):
                logo_path = os.path.join(sys._MEIPASS, "logo.png")
            else:
                logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
                if not os.path.exists(logo_path):
                    logo_path = os.path.join(os.path.abspath("."), "logo.png")

        try:
            if os.path.exists(logo_path):
                from PIL import Image, ImageTk
                img = Image.open(logo_path).convert("RGBA")
                img.thumbnail((200, 150), Image.LANCZOS)
                self._logo_img = ImageTk.PhotoImage(img)
        except Exception:
            pass
        # ───────────────────────────────────────────────────────────────────────────────

        self._build_ui()
        self._fit_window_to_content()
        self._load()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _safe_geometry(self, saved: str) -> str:
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        default_w, default_h = 900, 580

        if saved:
            m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", saved)
            if m:
                w, h, x, y = int(m[1]), int(m[2]), int(m[3]), int(m[4])
                if (x + 100 <= sw and y + 100 <= sh and x + w >= 100 and y + h >= 100):
                    w = min(w, sw)
                    h = min(h, sh)
                    return f"{w}x{h}+{x}+{y}"

        w = min(default_w, sw)
        h = min(default_h, sh)
        x = (sw - w) // 2
        y = (sh - h) // 2
        return f"{w}x{h}+{x}+{y}"

    def _fit_window_to_content(self):
        self.update_idletasks()
        toolbar_w = getattr(self, "_toolbar", self).winfo_reqwidth()
        sidebar_w = getattr(self, "_sidebar", self).winfo_reqwidth()
        min_w = max(900, toolbar_w + sidebar_w + 24)
        min_h = max(520, self.winfo_reqheight())

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        min_w = min(min_w, sw)
        min_h = min(min_h, sh - 40)
        self.minsize(min_w, min_h)

        m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", self.geometry())
        if not m:
            return
        w, h, x, y = map(int, m.groups())
        new_w = max(w, min_w)
        new_h = max(h, min_h)
        x = max(0, min(x, sw - new_w))
        y = max(0, min(y, sh - new_h))
        if (new_w, new_h) != (w, h):
            self.geometry(f"{new_w}x{new_h}+{x}+{y}")

    def _resize_start_drag(self, event):
        self._resize_start = (event.x_root, event.y_root, self.winfo_width(), self.winfo_height())

    def _resize_drag(self, event):
        if not self._resize_start:
            return
        start_x, start_y, start_w, start_h = self._resize_start
        min_w, min_h = self.minsize()
        new_w = max(min_w, start_w + event.x_root - start_x)
        new_h = max(min_h, start_h + event.y_root - start_y)
        self.geometry(f"{new_w}x{new_h}")

    def _on_close(self):
        if self._dirty:
            if not DarkDialog.ask(self, T("dlg_unsaved_title"), T("dlg_unsaved_msg")):
                return
        self._settings["geometry"] = self.geometry()
        self._settings["language"] = current_lang()
        save_settings(self._settings)
        self.destroy()

    def _build_ui(self):
        # ── Custom title bar ───────────────────────────────────────────────
        self._titlebar = CustomTitlebar(self, title="HOTS", on_close=self._on_close, on_minimize=self.iconify)
        self._titlebar.pack(fill="x", side="top")

        self._title_suffix = tk.Label(self._titlebar, text="Developed by Darsono", bg=self._titlebar["bg"], fg=DARK["fg2"], font=("Segoe UI", 9, "normal"))
        self._title_suffix.pack(side="left", padx=(2, 10))

        # ── Sidebar ────────────────────────────────────────────────────────
        self._sidebar = tk.Frame(self, bg=DARK["bg2"], width=180, highlightthickness=1, highlightbackground=DARK["border"])
        self._sidebar.pack(side="left", fill="y")
        sidebar = self._sidebar

        if self._logo_img:
            logo_lbl = tk.Label(sidebar, image=self._logo_img, bg=DARK["bg2"], cursor="arrow")
            logo_lbl.pack(padx=12, pady=(14, 6))
            tk.Frame(sidebar, bg=DARK["border"], height=1).pack(fill="x", padx=8, pady=(4, 10))

        make_btn(sidebar, "🛠", "#80d4ff", T("btn_repair"),    self._repair).pack(fill="x", padx=8, pady=(10, 4))
        make_btn(sidebar, "🧹", "#ffa060", T("btn_default"), self._restore_default).pack(fill="x", padx=8, pady=4)

        tk.Frame(sidebar, bg=DARK["border"], height=1).pack(fill="x", padx=8, pady=10)

        make_btn(sidebar, "\U0001f50d", "#80ffb0", T("btn_check_dom"), self._diag_existence).pack(fill="x", padx=8, pady=4)
        make_btn(sidebar, "\U0001f6e1", "#ff8080", T("btn_malware"), self._diag_malware).pack(fill="x", padx=8, pady=4)

        tk.Frame(sidebar, bg=DARK["border"], height=1).pack(fill="x", padx=8, pady=10)

        make_btn(sidebar, "🛡️", "#ff9f43", T("btn_parental"), self._open_parental_control).pack(fill="x", padx=8, pady=4)

        tk.Frame(sidebar, bg=DARK["border"], height=1).pack(fill="x", padx=8, pady=10)

        # ── Options (bottom of sidebar) ───────────────────────────────────
        sidebar_bottom = tk.Frame(sidebar, bg=DARK["bg2"])
        sidebar_bottom.pack(side="bottom", fill="x", padx=8, pady=(4, 10))

        tk.Frame(sidebar, bg=DARK["border"], height=1).pack(side="bottom", fill="x", padx=8, pady=(0, 2))

        self._options_panel = tk.Frame(sidebar, bg=DARK["bg2"], highlightthickness=1, highlightbackground=DARK["border"])
        self._options_visible = False

        def _make_option_btn(parent, icon, icon_color, label, cmd):
            f = tk.Frame(parent, bg=DARK["bg2"], cursor="hand2")
            f.pack(fill="x")
            inner = tk.Frame(f, bg=DARK["bg2"], cursor="hand2")
            inner.pack(fill="x", padx=8, pady=4)
            ico_lbl = tk.Label(inner, text=icon, bg=DARK["bg2"], fg=icon_color,
                               font=("Segoe UI Emoji", 13), cursor="hand2")
            ico_lbl.pack(side="left", padx=(2, 6))
            txt_lbl = tk.Label(inner, text=label, bg=DARK["bg2"], fg=DARK["fg"],
                               font=("Segoe UI", 9), anchor="w", cursor="hand2")
            txt_lbl.pack(side="left", fill="x", expand=True)

            def on_enter(_):
                for w in (f, inner, ico_lbl, txt_lbl):
                    w.config(bg=DARK["accent"])
                txt_lbl.config(fg=DARK["accent_fg"])
                ico_lbl.config(fg=icon_color)
            def on_leave(_):
                bg = DARK["accent"] if getattr(f, "_active", False) else DARK["bg2"]
                for w in (f, inner, ico_lbl, txt_lbl):
                    w.config(bg=bg)
                txt_lbl.config(fg=DARK["fg"])
                ico_lbl.config(fg=icon_color)
            for w in (f, inner, ico_lbl, txt_lbl):
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", lambda _, c=cmd: c())
            f._inner_widgets = (f, inner, ico_lbl, txt_lbl)
            f._icon_color = icon_color
            return f

        _make_option_btn(self._options_panel, "ℹ️", "#60c8ff", T("opt_about"),    self._about)
        tk.Frame(self._options_panel, bg=DARK["border"], height=1).pack(fill="x")
        _make_option_btn(self._options_panel, "❤️", "#e05050", T("opt_support"),  self._support)
        tk.Frame(self._options_panel, bg=DARK["border"], height=1).pack(fill="x")
        self._raw_view_btn = _make_option_btn(self._options_panel, "📋", "#80ffb0", T("opt_show_raw"), self._toggle_raw_view)
        tk.Frame(self._options_panel, bg=DARK["border"], height=1).pack(fill="x")
        self._pass_option_btn = _make_option_btn(self._options_panel, "🔒", "#ffd080", self._pass_btn_label(), self._manage_password)
        tk.Frame(self._options_panel, bg=DARK["border"], height=1).pack(fill="x")
        _make_option_btn(self._options_panel, "🌐", "#a0d0ff", T("opt_language"),  self._change_language)

        def _toggle_options_panel():
            if self._options_visible:
                self._options_panel.pack_forget()
                self._options_visible = False
            else:
                self._options_panel.pack(before=sidebar_bottom, fill="x", padx=8, pady=(0, 4))
                self._options_visible = True
                # Auto-expand window downward if needed
                self._fit_window_to_content()

        make_btn(sidebar_bottom, "⚙️", "#ffd080", T("btn_options"), _toggle_options_panel).pack(fill="x")

        # ── Main container ────────────────────────────────────────────────
        main_area = tk.Frame(self, bg=DARK["bg"])
        main_area.pack(side="left", fill="both", expand=True)

        # ── Toolbar ───────────────────────────────────────────────────────
        self._toolbar = tk.Frame(main_area, bg=DARK["bg2"], pady=8, padx=8, highlightthickness=1, highlightbackground=DARK["border"])
        self._toolbar.pack(fill="x")
        toolbar = self._toolbar

        for icon, icolor, label_key, cmd, acc in [
            ("➕", "#4ec94e", "btn_add",    self._add,    False),
            ("✏️", "#f0c040", "btn_edit",   self._edit,   False),
            ("⏻",  "#a0a0ff", "btn_toggle", self._toggle, False),
            ("🗑", "#e05050", "btn_delete", self._delete, False),
        ]:
            make_btn(toolbar, icon, icolor, T(label_key), cmd, acc).pack(side="left", padx=3)

        self._save_btn = make_btn(toolbar, "💾", "#60c8ff", T("btn_save"), self._save, accent=False)
        self._save_btn.pack(side="left", padx=3)
        self._dirty = False

        tk.Frame(toolbar, bg=DARK["border"], width=1).pack(side="left", fill="y", padx=8, pady=4)

        for icon, icolor, label_key, cmd in [
            ("📥", "#80d4ff", "btn_import",  self._import),
            ("📤", "#ffa060", "btn_export",  self._export),
            ("🗂", "#c0a0ff", "btn_backups", self._backups),
        ]:
            make_btn(toolbar, icon, icolor, T(label_key), cmd).pack(side="left", padx=3)

        # ── Context menu ──────────────────────────────────────────────────
        self.menu = tk.Menu(self, tearoff=0, bg=DARK["bg2"], fg=DARK["fg"], activebackground=DARK["accent"], activeforeground=DARK["accent_fg"], relief="flat", bd=0)
        self.menu.add_command(label=T("ctx_edit"),    command=self._edit)
        self.menu.add_command(label=T("ctx_delete"),  command=self._delete)
        self.menu.add_command(label=T("ctx_toggle"),  command=self._toggle)
        self.menu.add_separator()
        self.menu.add_command(label=T("ctx_zero_ip"), command=self._set_zero_ip)

        # ── Search bar ────────────────────────────────────────────────────
        search_bar = tk.Frame(main_area, bg=DARK["search_bg"], highlightthickness=1, highlightbackground=DARK["border"])
        search_bar.pack(fill="x")

        tk.Label(search_bar, text="🔍", bg=DARK["search_bg"], fg=DARK["fg2"], font=("Segoe UI Emoji", 12)).pack(side="left", padx=(10, 4), pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        se = tk.Entry(search_bar, textvariable=self.search_var, bg=DARK["search_bg"], fg=DARK["fg"], insertbackground=DARK["fg"], selectbackground=DARK["accent"], selectforeground=DARK["accent_fg"], relief="flat", bd=0, font=("Segoe UI", 10), highlightthickness=0)
        se.pack(side="left", fill="x", expand=True, pady=6)
        _add_paste_menu(se)

        self.search_count = tk.Label(search_bar, text="", bg=DARK["search_bg"], fg=DARK["fg2"], font=("Segoe UI", 9))
        self.search_count.pack(side="right", padx=10)

        clr = tk.Label(search_bar, text="\u2715", bg=DARK["search_bg"], fg=DARK["fg2"], font=("Segoe UI", 11), cursor="hand2")
        clr.pack(side="right", padx=(0, 4))
        clr.bind("<Button-1>", lambda _: self.search_var.set(""))

        # ── Table (Treeview) ──────────────────────────────────────────────
        frame = tk.Frame(main_area, bg=DARK["bg"])
        self._table_frame = frame
        frame.pack(fill="both", expand=True, padx=8, pady=(6, 0))

        self._raw_frame = tk.Frame(main_area, bg=DARK["bg"])
        self._raw_view_active = False

        cols = ("status", "ip", "hostname", "comment")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="extended")
        self.tree.heading("status",   text=T("col_status"),   command=lambda: self._sort_col("status"))
        self.tree.heading("ip",       text=T("col_ip"),       command=lambda: self._sort_col("ip"))
        self.tree.heading("hostname", text=T("col_hostname"), command=lambda: self._sort_col("hostname"))
        self.tree.heading("comment",  text=T("col_comment"),  command=lambda: self._sort_col("comment"))
        self.tree.column("status",   width=110, anchor="center", stretch=False)
        self.tree.column("ip",       width=160, stretch=False)
        self.tree.column("hostname", width=280)
        self.tree.column("comment",  width=210)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        vsb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.tag_configure("on",  foreground=DARK["green"])
        self.tree.tag_configure("off", foreground=DARK["gray"])
        self.tree.bind("<Double-1>", lambda _: self._edit())
        self.tree.bind("<Button-3>", self._show_context_menu)

        # ── Status bar ────────────────────────────────────────────────────
        tk.Label(main_area, anchor="e", text=T("hint_multiselect"), padx=10, pady=3, bg=DARK["bg2"], fg=DARK["fg2"], font=("Segoe UI", 8)).pack(fill="x", side="bottom")

        self.status_bar = tk.Label(main_area, anchor="w", padx=10, pady=4, bg=DARK["bg2"], fg=DARK["fg2"], font=("Segoe UI", 9), highlightthickness=1, highlightbackground=DARK["border"])
        self.status_bar.pack(fill="x", side="bottom")

        self._resize_grip = tk.Frame(self, bg=DARK["border"], width=14, height=14, cursor="size_nw_se")
        self._resize_grip.place(relx=1.0, rely=1.0, anchor="se")
        self._resize_grip.bind("<ButtonPress-1>", self._resize_start_drag)
        self._resize_grip.bind("<B1-Motion>", self._resize_drag)

    def _pass_btn_label(self) -> str:
        from .__main__ import _reg_get_password
        has = bool(_reg_get_password())
        return T("opt_pass_on") if has else T("opt_pass_off")

    def _refresh_pass_btn(self):
        """Refreshes the password button label after state change."""
        btn = getattr(self, "_pass_option_btn", None)
        if btn is None:
            return
        new_label = self._pass_btn_label()
        for w in btn.winfo_children():          # inner Frame
            for c in w.winfo_children():
                if isinstance(c, tk.Label) and str(c.cget("font")).endswith("9"):
                    c.config(text=new_label)
                    return

    def _manage_password(self):
        """Opens the set/remove password dialog."""
        if self._options_visible:
            self._options_panel.pack_forget()
            self._options_visible = False
        from .__main__ import _reg_get_password, _reg_set_password
        current_hash = _reg_get_password()

        def on_save(new_hash: str):
            _reg_set_password(new_hash)
            self._refresh_pass_btn()

        SetPasswordDialog(self, current_hash, on_save)

    def _change_language(self):
        """Opens the language selection dialog."""
        if self._options_visible:
            self._options_panel.pack_forget()
            self._options_visible = False

        dlg = tk.Toplevel(self)
        dlg.title(T("lang_title"))
        dlg.configure(bg=DARK["bg2"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.transient(self)

        # ── Header ────────────────────────────────────────────────────────
        hdr = tk.Frame(dlg, bg=DARK["accent"], height=4)
        hdr.pack(fill="x")

        tk.Label(dlg, text="🌐  " + T("lang_title"),
                 bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI", 11, "bold")).pack(pady=(16, 10), padx=24, anchor="w")

        tk.Frame(dlg, bg=DARK["border"], height=1).pack(fill="x", padx=16)

        # ── Radio buttons ─────────────────────────────────────────────────
        lang_var = tk.StringVar(value=current_lang())

        radio_frame = tk.Frame(dlg, bg=DARK["bg2"])
        radio_frame.pack(fill="x", padx=20, pady=(10, 4))

        flags = {"en": "🇬🇧", "pl": "🇵🇱", "fr": "🇫🇷"}
        for code, name in LANGUAGES.items():
            row = tk.Frame(radio_frame, bg=DARK["bg2"])
            row.pack(fill="x", pady=3)
            tk.Radiobutton(
                row, text=f"{flags.get(code, '')}  {name}",
                variable=lang_var, value=code,
                bg=DARK["bg2"], fg=DARK["fg"],
                selectcolor=DARK["bg3"],
                activebackground=DARK["bg2"], activeforeground=DARK["fg"],
                font=("Segoe UI", 10), cursor="hand2",
                indicatoron=True
            ).pack(side="left", padx=4)

        tk.Frame(dlg, bg=DARK["border"], height=1).pack(fill="x", padx=16, pady=(8, 0))

        # ── OK button ─────────────────────────────────────────────────────
        def _apply():
            chosen = lang_var.get()
            if chosen != current_lang():
                set_lang(chosen)
                self._settings["language"] = chosen
                save_settings(self._settings)
                dlg.destroy()
                DarkDialog.info(self, T("lang_title"), T("lang_restart_msg"))
            else:
                dlg.destroy()

        btn_frame = tk.Frame(dlg, bg=DARK["bg2"])
        btn_frame.pack(pady=14)
        make_btn(btn_frame, "✔", "#80ffb0", "OK", _apply, accent=True).pack()

        # ── Center dialog ─────────────────────────────────────────────────
        dlg.update_idletasks()
        w = max(dlg.winfo_reqwidth(), 280)
        h = max(dlg.winfo_reqheight(), 220)
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

    def _about(self):
        if self._options_visible:
            self._options_panel.pack_forget()
            self._options_visible = False

        dlg = tk.Toplevel(self)
        dlg.title("About – HOTS")
        dlg.configure(bg=DARK["bg"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.transient(self)
        dlg.overrideredirect(False)

        # ── Colored header ────────────────────────────────────────────────
        hdr = tk.Frame(dlg, bg=DARK["accent"], height=5)
        hdr.pack(fill="x")

        # ── Logo + title ──────────────────────────────────────────────────
        top = tk.Frame(dlg, bg=DARK["bg2"])
        top.pack(fill="x")

        title_col = tk.Frame(top, bg=DARK["bg2"])
        title_col.pack(side="left", fill="x", expand=True, padx=(20, 10), pady=18)

        tk.Label(title_col, text="HOTS",
                 bg=DARK["bg2"], fg=DARK["accent"],
                 font=("Segoe UI", 28, "bold")).pack(anchor="w")

        tk.Label(title_col, text=T("about_subtitle"),
                 bg=DARK["bg2"], fg=DARK["fg2"],
                 font=("Segoe UI", 11)).pack(anchor="w")

        tk.Label(title_col, text=T("about_version"),
                 bg=DARK["bg2"], fg=DARK["fg2"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))

        # ── Separator ──────────────────────────────────────────────────────
        tk.Frame(dlg, bg=DARK["border"], height=1).pack(fill="x", padx=16)

        # ── Description ───────────────────────────────────────────────────
        desc_frame = tk.Frame(dlg, bg=DARK["bg"])
        desc_frame.pack(fill="x", padx=20, pady=(14, 6))

        tk.Label(desc_frame,
                 text=T("about_desc"),
                 bg=DARK["bg"], fg=DARK["fg"],
                 font=("Segoe UI", 9),
                 justify="left").pack(anchor="w")

        # ── Features ──────────────────────────────────────────────────────
        tk.Frame(dlg, bg=DARK["border"], height=1).pack(fill="x", padx=16, pady=(10, 4))

        features_frame = tk.Frame(dlg, bg=DARK["bg"])
        features_frame.pack(fill="x", padx=20, pady=(4, 10))

        features = [
            ("🛡️", T("about_feat_parental")),
            ("🔍", T("about_feat_diag")),
            ("💾", T("about_feat_backup")),
            ("📋", T("about_feat_raw")),
            ("🔒", T("about_feat_password")),
            ("🌐", T("about_feat_lang")),
        ]

        col_left  = tk.Frame(features_frame, bg=DARK["bg"])
        col_right = tk.Frame(features_frame, bg=DARK["bg"])
        col_left.pack(side="left", fill="x", expand=True)
        col_right.pack(side="left", fill="x", expand=True)

        for i, (icon, label) in enumerate(features):
            col = col_left if i % 2 == 0 else col_right
            row = tk.Frame(col, bg=DARK["bg"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=icon, bg=DARK["bg"], fg=DARK["accent"],
                     font=("Segoe UI Emoji", 10)).pack(side="left", padx=(0, 6))
            tk.Label(row, text=label, bg=DARK["bg"], fg=DARK["fg"],
                     font=("Segoe UI", 9)).pack(side="left")

        # ── Separator ──────────────────────────────────────────────────────
        tk.Frame(dlg, bg=DARK["border"], height=1).pack(fill="x", padx=16, pady=(4, 0))

        # ── Footer: author + OK button ────────────────────────────────────
        footer = tk.Frame(dlg, bg=DARK["bg2"])
        footer.pack(fill="x")

        tk.Label(footer,
                 text=T("about_footer"),
                 bg=DARK["bg2"], fg=DARK["fg2"],
                 font=("Segoe UI", 8)).pack(side="left", padx=16, pady=12)

        ok_btn = make_btn(footer, "✔", "#60c8ff", T("about_close"), dlg.destroy, accent=False)
        ok_btn.pack(side="right", padx=12, pady=8)

        # ── Center dialog ────────────────────────────────────────────────
        dlg.update_idletasks()
        w = max(dlg.winfo_reqwidth(), 380)
        h = max(dlg.winfo_reqheight(), 320)
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

    def _toggle_raw_view(self):
        if self._options_visible:
            self._options_panel.pack_forget()
            self._options_visible = False

        if self._raw_view_active:
            self._raw_frame.pack_forget()
            self._table_frame.pack(fill="both", expand=True, padx=8, pady=(6, 0))
            self._raw_view_active = False
            self._refresh_tree()
            self._update_status()
        else:
            self._table_frame.pack_forget()
            self._raw_frame.pack(fill="both", expand=True, padx=8, pady=(6, 0))
            self._raw_view_active = True
            self._build_raw_view()

        btn = getattr(self, "_raw_view_btn", None)
        if btn:
            btn._active = self._raw_view_active
            active_bg = DARK["accent"] if self._raw_view_active else DARK["bg2"]
            for w in btn._inner_widgets:
                w.config(bg=active_bg)

    def _build_raw_view(self):
        for w in self._raw_frame.winfo_children():
            w.destroy()

        bar = tk.Frame(self._raw_frame, bg=DARK["bg2"], pady=6, padx=8, highlightthickness=1, highlightbackground=DARK["border"])
        bar.pack(fill="x")

        tk.Label(bar, text=T("raw_view_hint"), bg=DARK["bg2"], fg=DARK["fg2"], font=("Segoe UI", 9), anchor="w").pack(side="left", padx=(0, 16))

        editor_frame = tk.Frame(self._raw_frame, bg=DARK["bg"])
        editor_frame.pack(fill="both", expand=True, padx=8, pady=(6, 4))

        self._raw_line_nums = tk.Text(editor_frame, width=5, bg=DARK["bg2"], fg=DARK["fg2"], font=("Consolas", 11), relief="flat", bd=0, padx=6, state="disabled", cursor="arrow", highlightthickness=0, selectbackground=DARK["bg2"])
        self._raw_line_nums.pack(side="left", fill="y")

        tk.Frame(editor_frame, bg=DARK["border"], width=1).pack(side="left", fill="y")

        vsb = ttk.Scrollbar(editor_frame, orient="vertical")
        _hsb_style = ttk.Style()
        _hsb_style.configure("Dark.Horizontal.TScrollbar",
                             background=DARK["bg3"], troughcolor=DARK["bg"],
                             bordercolor=DARK["bg"], arrowcolor=DARK["fg2"])
        _hsb_style.map("Dark.Horizontal.TScrollbar",
                       background=[("active", DARK["accent"]), ("pressed", DARK["accent"])])
        hsb = ttk.Scrollbar(self._raw_frame, orient="horizontal",
                            style="Dark.Horizontal.TScrollbar")
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x", padx=8)

        self._raw_text = tk.Text(editor_frame, bg=DARK["bg"], fg=DARK["fg"], insertbackground=DARK["fg"], selectbackground=DARK["accent"], selectforeground=DARK["accent_fg"], font=("Consolas", 11), relief="flat", bd=0, padx=10, pady=4, wrap="none", undo=True, highlightthickness=0, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._raw_text.pack(side="left", fill="both", expand=True)

        vsb.config(command=self._raw_scroll_both)
        hsb.config(command=self._raw_text.xview)

        # ── TAG CONFIGURATION AND PRIORITY ────────────────────────────────
        self._raw_text.tag_configure("cur_line", background=DARK["bg2"])
        self._raw_text.tag_configure("comment", foreground=DARK["fg2"])
        self._raw_text.tag_configure("active",  foreground=DARK["green"])
        
        # Critical: selection (sel) must sit above current-line highlight and syntax colors
        self._raw_text.tag_raise("sel", "cur_line")
        self._raw_text.tag_raise("sel", "comment")
        self._raw_text.tag_raise("sel", "active")
        # ───────────────────────────────────────────────────────────────

        lines = []
        for entry in self.entries:
            if entry["enabled"] is None:
                lines.append(entry.get("raw", ""))
            elif entry["enabled"]:
                line = f"{entry['ip']}\t{entry['hostname']}"
                if entry.get("comment"):
                    line += f"\t# {entry['comment']}"
                lines.append(line)
            else:
                line = f"# {entry['ip']}\t{entry['hostname']}"
                if entry.get("comment"):
                    line += f"\t# {entry['comment']}"
                lines.append(line)

        content = "\n".join(lines)
        self._raw_text.insert("1.0", content)
        self._raw_text.edit_modified(False)
        self._raw_apply_highlighting()
        self._raw_update_line_nums()

        self._raw_text.bind("<<Modified>>",    self._raw_on_modified)
        self._raw_text.bind("<KeyRelease>",    self._raw_on_key)
        self._raw_text.bind("<ButtonRelease>", self._raw_on_key)

        def _select_line(event):
            """Click on a line number selects the entire line in the editor."""
            self._raw_text.focus_set()
            idx = self._raw_text.index(f"@0,{event.y}")
            line = idx.split(".")[0]
            
            self._raw_text.tag_remove("sel", "1.0", "end")
            self._raw_text.tag_add("sel", f"{line}.0", f"{line}.end+1c")
            self._raw_text.mark_set("insert", f"{line}.0")
            return "break"

        self._raw_line_nums.bind("<Button-1>", _select_line)
        self._raw_text.bind("<Triple-Button-1>", lambda e: (
            self._raw_text.tag_remove("sel", "1.0", "end"),
            self._raw_text.tag_add("sel",
                self._raw_text.index("insert linestart"),
                self._raw_text.index("insert lineend+1c")),
            "break"
        ))

    def _raw_scroll_both(self, *args):
        self._raw_text.yview(*args)
        self._raw_line_nums.yview(*args)

    def _raw_update_line_nums(self):
        self._raw_line_nums.config(state="normal")
        self._raw_line_nums.delete("1.0", "end")
        line_count = int(self._raw_text.index("end-1c").split(".")[0])
        nums = "\n".join(str(i) for i in range(1, line_count + 1))
        self._raw_line_nums.insert("1.0", nums)
        self._raw_line_nums.config(state="disabled")

    def _raw_apply_highlighting(self):
        txt = self._raw_text
        for tag in ("comment", "active"):
            txt.tag_remove(tag, "1.0", "end")
        line_count = int(txt.index("end-1c").split(".")[0])
        for ln in range(1, line_count + 1):
            line = txt.get(f"{ln}.0", f"{ln}.end").strip()
            if not line:
                continue
            if line.startswith("#"):
                txt.tag_add("comment", f"{ln}.0", f"{ln}.end")
            else:
                txt.tag_add("active", f"{ln}.0", f"{ln}.end")

    def _raw_on_key(self, _event=None):
        self._raw_text.tag_remove("cur_line", "1.0", "end")
        cur = self._raw_text.index("insert").split(".")[0]
        self._raw_text.tag_add("cur_line", f"{cur}.0", f"{cur}.end+1c")
        
        # Ensure selection (sel) keeps highest visual priority after every move/keystroke
        self._raw_text.tag_raise("sel", "cur_line")

        new_count = int(self._raw_text.index("end-1c").split(".")[0])
        if new_count != getattr(self, "_raw_last_line_count", -1):
            self._raw_last_line_count = new_count
            self._raw_update_line_nums()

        if hasattr(self, "_raw_hl_job"):
            self.after_cancel(self._raw_hl_job)
        self._raw_hl_job = self.after(120, self._raw_apply_highlighting)

    def _raw_on_modified(self, _event=None):
        if self._raw_text.edit_modified():
            self._mark_dirty()
            self._raw_text.edit_modified(False)

    def _show_context_menu(self, event):
        row = self.tree.identify_row(event.y)
        if not row:
            return
        if row not in self.tree.selection():
            self.tree.selection_set(row)
        self.menu.post(event.x_root, event.y_root)

    def _set_zero_ip(self):
        indices = self._selected_indices()
        if not indices:
            return
        for i in indices:
            if self.entries[i]["enabled"] is not None:
                self.entries[i]["ip"] = "0.0.0.0"
        self._refresh_tree()
        self._update_status()
        self._mark_dirty()

    def _sort_col(self, col):
        if not hasattr(self, "_sort_state"):
            self._sort_state = {}
        reverse = self._sort_state.get(col, False)
        self._sort_state = {col: not reverse}

        col_keys = {"status": "col_status", "ip": "col_ip", "hostname": "col_hostname", "comment": "col_comment"}
        for c, key in col_keys.items():
            self.tree.heading(c, text=T(key))
        arrow = " \u25b2" if not reverse else " \u25bc"
        self.tree.heading(col, text=T(col_keys[col]) + arrow)

        self._sort_col_active  = col
        self._sort_col_reverse = reverse
        self._refresh_tree()

    def _sort_key_for(self, col, e):
        if col == "ip":
            return tuple(int(x) if x.isdigit() else x for x in re.split(r"(\d+)", e["ip"]))
        if col == "status":
            return 0 if e["enabled"] else 1
        return str(e.get(col, "")).lower()

    def _on_search(self, *_):
        self._refresh_tree()

    def _mark_dirty(self):
        if not self._dirty:
            self._dirty = True
            self._save_btn._base_bg = DARK["accent"]
            for w in [self._save_btn] + self._save_btn.winfo_children():
                w.configure(bg=DARK["accent"])
            for w in self._save_btn.winfo_children():
                w.configure(fg="#ffffff")

    def _mark_clean(self):
        if self._dirty:
            self._dirty = False
            self._save_btn._base_bg = DARK["btn_bg"]
            for w in [self._save_btn] + self._save_btn.winfo_children():
                w.configure(bg=DARK["btn_bg"])
            for w in self._save_btn.winfo_children():
                w.configure(fg="#60c8ff")

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        query = self.search_var.get().lower().strip() if hasattr(self, "search_var") else ""
        total_real = sum(1 for e in self.entries if e["enabled"] is not None)

        visible = [
            (i, e) for i, e in enumerate(self.entries)
            if e["enabled"] is not None and (not query or any(query in str(e.get(f, "")).lower() for f in ("ip", "hostname", "comment")))
        ]

        col     = getattr(self, "_sort_col_active",  None)
        reverse = getattr(self, "_sort_col_reverse", False)
        if col:
            visible.sort(key=lambda pair: self._sort_key_for(col, pair[1]), reverse=reverse)

        for i, e in visible:
            tag   = "on" if e["enabled"] else "off"
            label = "✔ active" if e["enabled"] else "✘ disabled"
            if current_lang() == "pl":
                label = "✔ aktywny" if e["enabled"] else "✘ wyłączony"
            elif current_lang() == "fr":
                label = "✔ actif" if e["enabled"] else "✘ désactivé"
            self.tree.insert("", "end", iid=str(i), values=(label, e["ip"], e["hostname"], e["comment"]), tags=(tag,))

        shown = len(visible)
        self.search_count.config(text=f"{shown} / {total_real}" if query else "")

    def _load(self):
        self.entries = parse_hosts(HOSTS_PATH)
        self._sort_state      = {}
        self._sort_col_active  = None
        self._sort_col_reverse = False
        col_keys = {"status": "col_status", "ip": "col_ip", "hostname": "col_hostname", "comment": "col_comment"}
        for c, key in col_keys.items():
            try: self.tree.heading(c, text=T(key))
            except Exception: pass
        self._refresh_tree()
        self._update_status()

    def _reload(self):
        self._load()

    def _update_status(self):
        real = [e for e in self.entries if e["enabled"] is not None]
        on   = sum(1 for e in real if e["enabled"])
        baks = len(list_backups(HOSTS_PATH))
        off  = len(real) - on
        self.status_bar.config(text=f"{HOSTS_PATH}   |   {T('status_entries', total=len(real), active=on, disabled=off)}   |   Backups: {baks}")

    def _selected_idx(self):
        for s in self.tree.selection():
            idx = int(s)
            if self.entries[idx]["enabled"] is not None: return idx
        return None

    def _selected_indices(self):
        return [int(s) for s in self.tree.selection() if self.entries[int(s)]["enabled"] is not None]

    def _add(self):
        existing = {e["hostname"].lower() for e in self.entries if e["enabled"] is not None}
        dlg = EntryDialog(self, existing_hostnames=existing)
        if dlg.result_list is not None:
            self.entries.extend(dlg.result_list)
            self._refresh_tree(); self._update_status(); self._mark_dirty()
        elif dlg.result:
            self.entries.append(dlg.result)
            self._refresh_tree(); self._update_status(); self._mark_dirty()

    def _edit(self):
        idx = self._selected_idx()
        if idx is None:
            DarkDialog.info(self, T("no_sel_title"), T("no_sel_edit"))
            return
        dlg = EntryDialog(self, self.entries[idx])
        if dlg.result:
            self.entries[idx] = dlg.result
            self._refresh_tree(); self._update_status(); self._mark_dirty()

    def _toggle(self):
        indices = self._selected_indices()
        if not indices:
            DarkDialog.info(self, T("no_sel_title"), T("no_sel_toggle"))
            return
        any_off = any(not self.entries[i]["enabled"] for i in indices)
        for i in indices:
            self.entries[i]["enabled"] = any_off
        self._refresh_tree(); self._update_status(); self._mark_dirty()

    def _delete(self):
        # In raw (notepad) view: delete selected text or current line
        if getattr(self, "_raw_view_active", False):
            try:
                if self._raw_text.tag_ranges("sel"):
                    self._raw_text.delete("sel.first", "sel.last")
                    self._raw_on_key()
                    self._mark_dirty()
                else:
                    DarkDialog.info(self, T("no_sel_title"), T("no_sel_raw_delete"))
            except Exception:
                pass
            return

        # Default delete logic for table (Treeview) view
        indices = self._selected_indices()
        if not indices:
            DarkDialog.info(self, T("no_sel_title"), T("no_sel_delete"))
            return
        if len(indices) == 1:
            e = self.entries[indices[0]]
            q = T("del_confirm_one", ip=e['ip'], hostname=e['hostname'])
        else:
            preview = "\n".join(f"{self.entries[i]['ip']}  {self.entries[i]['hostname']}" for i in indices[:10])
            suffix = T("del_more", n=len(indices)-10) if len(indices) > 10 else ""
            q = T("del_confirm_many", n=len(indices), preview=preview, suffix=suffix)
        if not DarkDialog.ask(self, T("del_confirm_title"), q): return
        for i in sorted(indices, reverse=True):
            self.entries.pop(i)
        self._refresh_tree(); self._update_status(); self._mark_dirty()

    def _save(self):
        if getattr(self, "_raw_view_active", False):
            import tempfile, os
            from .core import parse_hosts as _parse_hosts
            raw_text = self._raw_text.get("1.0", "end-1c")
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".hosts", delete=False) as tf:
                tf.write(raw_text)
                tmp_path = tf.name
            try: self.entries = _parse_hosts(tmp_path)
            except Exception as ex: DarkDialog.error(self, T("parse_err_title"), str(ex)); return
            finally:
                try: os.unlink(tmp_path)
                except Exception: pass

        # ── ENTRY LIMIT (> 20 000) ──
        active_count = sum(1 for e in self.entries if e.get("enabled") is True)
        if active_count > 20000:
            DarkDialog.error(self, T("save_limit_title"), T("save_limit_msg", n=active_count))
            return

        try:
            with open(HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f: old_text = f.read()
        except Exception: old_text = ""
        new_text = entries_to_text(self.entries)

        def do_save():
            self.status_bar.config(text=T("status_saving"))
            self.update_idletasks()

            def bg_save_worker():
                try:
                    dns_ok = save_hosts(HOSTS_PATH, self.entries)
                    self.after(0, lambda: save_success(dns_ok))
                except PermissionError:
                    self.after(0, save_permission_error)
                except Exception as ex:
                    self.after(0, lambda: DarkDialog.error(self, T("save_err_title"), str(ex)))
                finally:
                    self.after(0, self._update_status)

            def save_success(dns_ok):
                self._mark_clean()
                dns_line = T("save_dns_ok") if dns_ok else T("save_dns_slow")
                DarkDialog.info(self, T("save_success_title"), T("save_success_msg", dns_line=dns_line))

            def save_permission_error():
                DarkDialog.error(self, T("save_perm_title"), T("save_perm_msg"))

            threading.Thread(target=bg_save_worker, daemon=True).start()

        DiffDialog(self, old_text, new_text, on_confirm=do_save)

    def _import(self):
        result = import_hosts_file(self, self.entries)
        if result is not None:
            self.entries = result
            self._refresh_tree(); self._update_status(); self._mark_dirty()

    def _export(self):
        selected_indices = self._selected_indices()
        entries_to_export = [self.entries[i] for i in selected_indices] if selected_indices else self.entries
        export_count      = len(entries_to_export)
        total_count       = sum(1 for e in self.entries if e["enabled"] is not None)
        is_selection      = bool(selected_indices)

        # ── Export options dialog ─────────────────────────────────────────
        dlg = tk.Toplevel(self)
        dlg.title(T("btn_export"))
        dlg.configure(bg=DARK["bg2"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.transient(self)

        tk.Frame(dlg, bg=DARK["accent"], height=4).pack(fill="x")

        tk.Label(dlg, text="📤  " + T("btn_export"),
                 bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI", 11, "bold")).pack(pady=(16, 6), padx=24, anchor="w")

        tk.Frame(dlg, bg=DARK["border"], height=1).pack(fill="x", padx=16)

        # ── Export scope ──────────────────────────────────────────────────
        scope_frame = tk.Frame(dlg, bg=DARK["bg2"])
        scope_frame.pack(fill="x", padx=20, pady=(12, 4))

        tk.Label(scope_frame, text=T("export_scope_label"),
                 bg=DARK["bg2"], fg=DARK["fg2"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")

        scope_var = tk.StringVar(value="selection" if is_selection else "all")

        rb_all = tk.Radiobutton(
            scope_frame,
            text=T("export_scope_all", n=total_count),
            variable=scope_var, value="all",
            bg=DARK["bg2"], fg=DARK["fg"],
            selectcolor=DARK["bg3"],
            activebackground=DARK["bg2"], activeforeground=DARK["fg"],
            font=("Segoe UI", 10), cursor="hand2"
        )
        rb_all.pack(anchor="w", pady=(4, 1))

        rb_sel_text = T("export_scope_sel", n=export_count) if is_selection else T("export_scope_sel_none")
        rb_sel = tk.Radiobutton(
            scope_frame,
            text=rb_sel_text,
            variable=scope_var, value="selection",
            state="normal" if is_selection else "disabled",
            bg=DARK["bg2"], fg=DARK["fg"] if is_selection else DARK["fg2"],
            selectcolor=DARK["bg3"],
            activebackground=DARK["bg2"], activeforeground=DARK["fg"],
            font=("Segoe UI", 10), cursor="hand2" if is_selection else "arrow"
        )
        rb_sel.pack(anchor="w", pady=1)

        tk.Frame(dlg, bg=DARK["border"], height=1).pack(fill="x", padx=16, pady=(10, 0))

        # ── Comments option ───────────────────────────────────────────────
        comment_frame = tk.Frame(dlg, bg=DARK["bg2"])
        comment_frame.pack(fill="x", padx=20, pady=(10, 4))

        tk.Label(comment_frame, text=T("export_comments_label"),
                 bg=DARK["bg2"], fg=DARK["fg2"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")

        comments_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            comment_frame,
            text=T("export_comments_include"),
            variable=comments_var,
            bg=DARK["bg2"], fg=DARK["fg"],
            selectcolor=DARK["bg3"],
            activebackground=DARK["bg2"], activeforeground=DARK["fg"],
            font=("Segoe UI", 10), cursor="hand2"
        ).pack(anchor="w", pady=(4, 0))

        tk.Frame(dlg, bg=DARK["border"], height=1).pack(fill="x", padx=16, pady=(10, 0))

        # ── Buttons ───────────────────────────────────────────────────────
        btn_frame = tk.Frame(dlg, bg=DARK["bg2"])
        btn_frame.pack(pady=14)

        confirmed = [False]

        def _do_export():
            confirmed[0] = True
            dlg.destroy()

        make_btn(btn_frame, "📤", "#ffa060", T("btn_export"), _do_export, accent=True).pack(side="left", padx=6)
        make_btn(btn_frame, "✖", "#e05050", T("btn_cancel"), dlg.destroy).pack(side="left", padx=6)

        dlg.bind("<Return>", lambda _: _do_export())
        dlg.bind("<Escape>", lambda _: dlg.destroy())

        dlg.update_idletasks()
        w = max(dlg.winfo_reqwidth(), 320)
        h = max(dlg.winfo_reqheight(), 220)
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        dlg.wait_window()

        if not confirmed[0]:
            return

        # ── Perform the export ────────────────────────────────────────────
        if scope_var.get() == "selection" and is_selection:
            data = entries_to_export
        else:
            data = self.entries

        include_comments = comments_var.get()
        export_hosts(self, data, include_comments=include_comments)

    def _backups(self):
        BackupManagerDialog(self, HOSTS_PATH, on_restore=self._load)

    def _open_parental_control(self):
        """Opens the parental control dialog."""
        ParentalDialog(self)

    def _support(self):
        """Opens the project support dialog."""
        SupportDialog(self)

    def _diag_existence(self):
        selected = self._selected_indices()
        if not selected:
            DarkDialog.info(self, T("no_sel_title"), T("no_sel_check"))
            return
        to_check = [self.entries[i] for i in selected]
        DiagnosticsDialog(self, to_check, mode="existence", on_remove=self._remove_by_hostnames)

    def _diag_malware(self):
        selected = self._selected_indices()
        to_check = [self.entries[i] for i in selected] if selected else self.entries
        DiagnosticsDialog(self, to_check, mode="malware", on_remove=self._remove_by_hostnames)

    def _remove_by_hostnames(self, hostnames: set):
        self.entries = [e for e in self.entries if e["hostname"].lower() not in hostnames]
        self._refresh_tree(); self._update_status(); self._mark_dirty()

    def _repair(self):
        original_state = [(e.get("ip", ""), e.get("hostname", ""), e.get("comment", ""), e.get("enabled")) for e in self.entries]
        fixed_entries = []
        seen_pairs = set()
        wildcards_fixed = 0; dups_removed = 0; invalid_removed = 0; normalized = 0

        for e in self.entries:
            if e["enabled"] is None:
                fixed_entries.append(e); continue
            ip = e["ip"].strip(); host = e["hostname"].strip(); comment = e["comment"].strip()
            if not ip or not host or not is_valid_ip(ip):
                invalid_removed += 1; continue

            # Strip wildcard prefix (*.example.com → example.com)
            original_host = host
            host = re.sub(r"^\*\.?", "", host).lstrip(".")
            if host != original_host: wildcards_fixed += 1
            if not host: invalid_removed += 1; continue

            # Normalize hostname to lowercase — tracked by a separate counter
            host_clean = host.lower().strip()
            if host_clean != host and host == original_host:
                # Case-only change (no wildcard involved) — count separately
                normalized += 1

            # Duplicate key includes enabled state to avoid merging active
            # and disabled entries (different semantics despite same IP+hostname)
            pair_key = (ip.strip(), host_clean, bool(e["enabled"]))

            if pair_key in seen_pairs:
                dups_removed += 1
                if comment:
                    for prev in reversed(fixed_entries):
                        if (prev["enabled"] is not None
                                and bool(prev["enabled"]) == bool(e["enabled"])
                                and prev["ip"].strip() == ip.strip()
                                and prev["hostname"].lower() == host_clean):
                            if prev["comment"]:
                                if comment not in prev["comment"]: prev["comment"] += f" | {comment}"
                            else: prev["comment"] = comment
                            break
                continue
            seen_pairs.add(pair_key)
            fixed_entries.append({"enabled": e["enabled"], "ip": ip, "hostname": host_clean, "comment": comment, "raw": ""})

        new_state = [(e.get("ip", ""), e.get("hostname", ""), e.get("comment", ""), e.get("enabled")) for e in fixed_entries]
        if new_state == original_state:
            DarkDialog.info(self, T("repair_no_changes_title"), T("repair_no_changes_msg"))
            return

        self.entries = fixed_entries
        self._refresh_tree(); self._update_status(); self._mark_dirty()

        report = [T("repair_done_header")]
        if wildcards_fixed: report.append(T("repair_wildcards",   n=wildcards_fixed))
        if dups_removed:    report.append(T("repair_dups",        n=dups_removed))
        if invalid_removed: report.append(T("repair_invalid",     n=invalid_removed))
        if normalized:      report.append(T("repair_normalized",  n=normalized))
        DarkDialog.info(self, T("repair_done_title"), "\n".join(report))

    def _restore_default(self):
        if not DarkDialog.ask(self, T("restore_ask_title"), T("restore_ask_msg")): return

        # Default entries — without the historical header boilerplate
        default_entries = [
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# Copyright (c) 1993-2014 Microsoft Corp."},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "#"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# This is a sample HOSTS file used by Microsoft TCP/IP for Windows."},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "#"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# localhost name resolution is handled within DNS itself."},
            {"enabled": True,  "ip": "127.0.0.1", "hostname": "localhost", "comment": "", "raw": ""},
            {"enabled": True,  "ip": "::1",        "hostname": "localhost", "comment": "", "raw": ""},
        ]

        try:
            # save_hosts() handles: write via temp file + cmd copy,
            # backup rotation (max 10) and DNS flush — consistent with the rest of the app
            dns_ok = save_hosts(HOSTS_PATH, default_entries)
        except Exception as ex:
            DarkDialog.error(self, T("save_err_title"), str(ex))
            return

        self._load()
        dns_line = T("save_dns_ok") if dns_ok else T("save_dns_slow")
        DarkDialog.info(self, T("restore_done_title"), T("restore_done_msg") + f"\n{dns_line}")