"""
Reusable UI components: buttons, fields, dialogs, dark theme.
To change button appearance or colors, edit this file.
"""

import tkinter as tk
from tkinter import ttk

from .constants import DARK


# ── Custom title bar ───────────────────────────────────────────────────────
class CustomTitlebar(tk.Frame):
    _HEIGHT = 38

    def __init__(self, parent, title="HOTS", on_close=None, on_minimize=None):
        super().__init__(parent, bg=DARK["bg2"], height=self._HEIGHT)
        self.pack_propagate(False)
        self._parent   = parent
        self._on_close = on_close
        self._on_min   = on_minimize
        self._drag_x   = 0
        self._drag_y   = 0
        self._maximized   = False
        self._restore_geo = None

        tk.Frame(self, bg=DARK["accent"], width=3).pack(side="left", fill="y")

        self._title_lbl = tk.Label(
            self, text=title,
            bg=DARK["bg2"], fg="#d4a017",
            font=("Segoe UI", 13, "bold"),
            padx=14, pady=0)
        self._title_lbl.pack(side="left", fill="y")

        btn_frame = tk.Frame(self, bg=DARK["bg2"])
        btn_frame.pack(side="right", fill="y")

        self._close_btn = self._make_wm_btn(
            btn_frame, "✕", DARK["fg2"], "#c84040", "#3a1010", self._close)
        self._close_btn.pack(side="right", fill="y")

        self._max_btn = self._make_wm_btn(
            btn_frame, "□", DARK["fg2"], DARK["fg"], DARK["bg3"], self._toggle_maximize)
        self._max_btn.pack(side="right", fill="y")

        self._min_btn = self._make_wm_btn(
            btn_frame, "─", DARK["fg2"], DARK["fg"], DARK["bg3"], self._minimize)
        self._min_btn.pack(side="right", fill="y")

        for w in (self, self._title_lbl):
            w.bind("<ButtonPress-1>",   self._drag_start)
            w.bind("<B1-Motion>",       self._drag_move)
            w.bind("<Double-Button-1>", self._toggle_maximize)

    @staticmethod
    def _make_wm_btn(parent, symbol, fg_normal, fg_hover, bg_hover, cmd):
        lbl = tk.Label(parent, text=symbol, bg=DARK["bg2"], fg=fg_normal,
                       font=("Segoe UI", 11), width=4, cursor="hand2")
        lbl.bind("<Enter>",    lambda _: lbl.configure(bg=bg_hover,    fg=fg_hover))
        lbl.bind("<Leave>",    lambda _: lbl.configure(bg=DARK["bg2"], fg=fg_normal))
        lbl.bind("<Button-1>", lambda _: cmd())
        return lbl

    def _close(self):
        if self._on_close:
            self._on_close()
        else:
            self._parent.destroy()

    def _minimize(self):
        self._parent.overrideredirect(False)
        self._parent.title("HOTS")
        _restore_icon(self._parent)
        # <Map> fires when window is RESTORED from taskbar, not when minimizing
        self._parent.bind("<Map>", self._on_restore_from_minimize)
        self._parent.iconify()

    def _on_restore_from_minimize(self, _=None):
        # state() is "normal" only after actual restore — prevents flicker loop
        if self._parent.state() != "iconic":
            self._parent.unbind("<Map>")
            self._parent.overrideredirect(True)
            self._parent.lift()

    def _toggle_maximize(self, _=None):
        if self._maximized:
            self._parent.geometry(self._restore_geo)
            self._max_btn.configure(text="□")
            self._maximized = False
        else:
            self._restore_geo = self._parent.geometry()
            try:
                import ctypes
                rc = ctypes.wintypes.RECT()
                ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rc), 0)
                w  = rc.right  - rc.left
                h  = rc.bottom - rc.top
                ox = rc.left
                oy = rc.top
            except Exception:
                sw = self._parent.winfo_screenwidth()
                sh = self._parent.winfo_screenheight()
                w, h, ox, oy = sw, sh - 48, 0, 0
            self._parent.geometry(f"{w}x{h}+{ox}+{oy}")
            self._max_btn.configure(text="❐")
            self._maximized = True

    def _drag_start(self, event):
        if self._maximized:
            return
        self._drag_x = event.x_root - self._parent.winfo_x()
        self._drag_y = event.y_root - self._parent.winfo_y()

    def _drag_move(self, event):
        if self._maximized:
            return
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self._parent.geometry(f"+{x}+{y}")


def _restore_icon(win):
    """Sets the window icon (logo.ico or logo.png) — needed after overrideredirect(False)."""
    import os, sys
    base = getattr(sys, '_MEIPASS', None) or os.path.dirname(os.path.abspath(__file__))
    try:
        ico = os.path.join(base, 'logo.ico')
        if os.path.exists(ico):
            win.iconbitmap(ico)
            return
    except Exception:
        pass
    try:
        from PIL import Image, ImageTk
        png = os.path.join(base, 'logo.png')
        if os.path.exists(png):
            img   = Image.open(png).resize((32, 32), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            win.iconphoto(True, photo)
            win._taskbar_icon = photo
    except Exception:
        pass


def center_on_parent(win, parent, min_w=0, min_h=0):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    req_w = max(win.winfo_reqwidth(),  min_w)
    req_h = max(win.winfo_reqheight(), min_h)
    w = min(req_w, sw - 40)
    h = min(req_h, sh - 80)
    px = parent.winfo_rootx() + parent.winfo_width()  // 2
    py = parent.winfo_rooty() + parent.winfo_height() // 2
    x = max(0, min(px - w // 2, sw - w - 20))
    y = max(0, min(py - h // 2, sh - h - 60))
    win.geometry(f"{w}x{h}+{x}+{y}")


# ── Dark dialogs ───────────────────────────────────────────────────────────
class DarkDialog:
    """Replaces standard messageboxes with dark-themed dialogs matching the app style."""

    @staticmethod
    def _make(parent, title, message, buttons, icon="ℹ"):
        # Lazy import of T — avoids circular import at startup
        from .i18n import T
        result = [None]
        win = tk.Toplevel(parent)
        win.title(title)
        win.configure(bg=DARK["bg2"])
        win.resizable(False, False)
        win.transient(parent)
        win.grab_set()

        body = tk.Frame(win, bg=DARK["bg2"])
        body.pack(padx=20, pady=(18, 10), fill="x")
        tk.Label(body, text=icon, bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI Emoji", 22)).pack(side="left", padx=(0, 14), anchor="n")
        tk.Label(body, text=message, bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI", 10), justify="left",
                 wraplength=360).pack(side="left", anchor="w")

        bf = tk.Frame(win, bg=DARK["bg2"])
        bf.pack(pady=(4, 16))
        for label, val in buttons:
            accent = val is True or val == "ok"
            b = make_btn(bf, "", DARK["accent_fg"], label,
                         lambda v=val: (result.__setitem__(0, v), win.destroy()),
                         accent=accent)
            b.pack(side="left", padx=6)

        win.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width()  // 2
        ph = parent.winfo_rooty() + parent.winfo_height() // 2
        ww = win.winfo_width()
        wh = win.winfo_height()
        win.geometry(f"+{pw - ww//2}+{ph - wh//2}")
        win.wait_window()
        return result[0]

    @classmethod
    def info(cls, parent, title, message):
        from .i18n import T
        cls._make(parent, title, message, [(T("btn_ok"), "ok")], icon="ℹ")

    @classmethod
    def error(cls, parent, title, message):
        from .i18n import T
        cls._make(parent, title, message, [(T("btn_ok"), "ok")], icon="✖")

    @classmethod
    def warning(cls, parent, title, message):
        from .i18n import T
        cls._make(parent, title, message, [(T("btn_ok"), "ok")], icon="⚠")

    @classmethod
    def ask(cls, parent, title, message):
        from .i18n import T
        return cls._make(parent, title, message,
                         [(T("btn_yes"), True), (T("btn_no"), False)], icon="?") is True


# ── Dark theme ─────────────────────────────────────────────────────────────
def apply_dark_style(root):
    root.configure(bg=DARK["bg"])
    s = ttk.Style(root)
    s.theme_use("default")
    s.configure("Treeview",
        background=DARK["bg2"], foreground=DARK["fg"],
        fieldbackground=DARK["bg2"], borderwidth=0,
        rowheight=28, font=("Segoe UI", 10))
    s.configure("Treeview.Heading",
        background=DARK["bg3"], foreground=DARK["fg2"],
        relief="flat", font=("Segoe UI", 9, "bold"))
    s.map("Treeview",
        background=[("selected", DARK["sel_bg"])],
        foreground=[("selected", DARK["sel_fg"])])
    s.map("Treeview.Heading", background=[("active", DARK["bg3"])])
    s.configure("Vertical.TScrollbar",
        background=DARK["bg3"], troughcolor=DARK["bg"],
        bordercolor=DARK["bg"], arrowcolor=DARK["fg2"])
    for name in ("Backup", "Diff"):
        s.configure(f"{name}.Treeview",
            background=DARK["bg2"], foreground=DARK["fg"],
            fieldbackground=DARK["bg2"], borderwidth=0,
            rowheight=22,
            font=("Cascadia Code", 9) if name == "Diff" else ("Segoe UI", 9))
        s.configure(f"{name}.Treeview.Heading",
            background=DARK["bg3"], foreground=DARK["fg2"],
            relief="flat", font=("Segoe UI", 9, "bold"))
        s.map(f"{name}.Treeview",
            background=[("selected", DARK["sel_bg"])],
            foreground=[("selected", DARK["sel_fg"])])
    s.configure("Diag.Treeview",
        background=DARK["bg2"], foreground=DARK["fg"],
        fieldbackground=DARK["bg2"], borderwidth=0,
        rowheight=24, font=("Segoe UI", 9))
    s.configure("Diag.Treeview.Heading",
        background=DARK["bg3"], foreground=DARK["fg2"],
        relief="flat", font=("Segoe UI", 9, "bold"))
    s.map("Diag.Treeview",
        background=[("selected", DARK["sel_bg"])],
        foreground=[("selected", DARK["sel_fg"])])


# ── Button ─────────────────────────────────────────────────────────────────
def make_btn(parent, icon, icon_color, label, command, accent=False):
    bg = DARK["accent"] if accent else DARK["btn_bg"]
    fg_txt = DARK["accent_fg"] if accent else DARK["fg2"]
    frame = tk.Frame(parent, bg=bg, cursor="hand2",
                     highlightthickness=1, highlightbackground=DARK["border"])
    li = tk.Label(frame, text=icon, bg=bg,
                  fg="#ffffff" if accent else icon_color,
                  font=("Segoe UI Emoji", 13), padx=0, pady=0)
    li.pack(side="left", padx=(10, 3), pady=6)
    lt = tk.Label(frame, text=label, bg=bg, fg=fg_txt,
                  font=("Segoe UI", 9), padx=0, pady=0)
    lt.pack(side="left", padx=(0, 12), pady=6)

    def _current_bg():
        return frame.cget("bg")

    def _hover_color():
        cb = _current_bg()
        if cb == DARK["accent"]:   return "#005fa3"
        if cb == DARK["btn_bg"]:   return DARK["btn_hover"]
        return "#005fa3" if cb not in (DARK["btn_hover"], DARK["bg3"]) else DARK["btn_hover"]

    def _enter(_):
        c = _hover_color()
        for w in (frame, li, lt): w.configure(bg=c)

    def _leave(_):
        base = getattr(frame, "_base_bg", _current_bg())
        for w in (frame, li, lt): w.configure(bg=base)

    def _click(_): command()

    for w in (frame, li, lt):
        w.bind("<Enter>",    _enter)
        w.bind("<Leave>",    _leave)
        w.bind("<Button-1>", _click)

    frame._base_bg = bg
    return frame


# ── Text entry ─────────────────────────────────────────────────────────────
def dark_entry(parent, textvariable, width=28):
    e = tk.Entry(parent, textvariable=textvariable, width=width,
                 bg=DARK["bg3"], fg=DARK["fg"],
                 insertbackground=DARK["fg"],
                 selectbackground=DARK["accent"],
                 selectforeground=DARK["accent_fg"],
                 relief="flat", bd=5,
                 highlightthickness=1,
                 highlightcolor=DARK["accent"],
                 highlightbackground=DARK["border"],
                 font=("Segoe UI", 10))
    _add_paste_menu(e)
    return e


def _add_paste_menu(w):
    """Adds a right-click context menu (Cut/Copy/Paste) to an Entry widget."""
    from .i18n import T
    m = tk.Menu(w, tearoff=0, bg=DARK["bg2"], fg=DARK["fg"],
                activebackground=DARK["accent"],
                activeforeground=DARK["accent_fg"], relief="flat")
    m.add_command(label=T("ctx_cut"),        command=lambda: w.event_generate("<<Cut>>"))
    m.add_command(label=T("ctx_copy"),       command=lambda: w.event_generate("<<Copy>>"))
    m.add_command(label=T("ctx_paste"),      command=lambda: w.event_generate("<<Paste>>"))
    m.add_separator()
    m.add_command(label=T("ctx_select_all"), command=lambda: w.select_range(0, "end"))
    w.bind("<Button-3>", lambda ev: (w.focus_set(), m.tk_popup(ev.x_root, ev.y_root)))
    w.bind("<Control-v>", lambda e: w.event_generate("<<Paste>>"))
    w.bind("<Control-V>", lambda e: w.event_generate("<<Paste>>"))


def field_lbl(parent, text, row):
    tk.Label(parent, text=text, bg=DARK["bg2"], fg=DARK["fg2"],
             font=("Segoe UI", 9)).grid(row=row, column=0, sticky="e", padx=12, pady=7)
