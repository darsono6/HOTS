"""
Reusable UI components: buttons, fields, dialogs, dark theme.
To change button appearance or colors, edit this file.
"""

import sys
import tkinter as tk
from tkinter import ttk

from .constants import DARK


def enable_rounded_corners(win):
    """Applies Windows 11 DWM rounded corners and a soft native drop
    shadow to an overrideredirect() Tk window (main window or any
    DarkToplevel dialog).

    Safe no-op on Windows 10 and non-Windows platforms: DWM there either
    doesn't expose the rounded-corner attribute or ignores it, so nothing
    breaks — the window just keeps square corners, same as before this
    function existed. The shadow works wherever DWM composition is
    active (Vista and up — effectively always, since it can't be turned
    off on Windows 8+).
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id())

        # ── Rounded corners (Windows 11 build 22000+) ───────────────────────
        # DWMWCP_ROUND = noticeable radius. Use DWMWCP_ROUNDSMALL (3)
        # instead for a more subtle rounding.
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_ROUND = 2
        pref = ctypes.c_int(DWMWCP_ROUND)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd), DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(pref), ctypes.sizeof(pref))

        # ── Soft native drop shadow ──────────────────────────────────────────
        # overrideredirect() creates a borderless (WS_POPUP-style) window,
        # which DWM doesn't shadow automatically. DwmExtendFrameIntoClientArea
        # with a near-zero margin tricks DWM into thinking the window has a
        # frame, so it renders its normal soft shadow — the same one every
        # ordinary bordered Win32 window gets for free. This replaces the
        # older CS_DROPSHADOW class style, which gives a small, hard-edged
        # shadow that tends to look like a flat outline rather than a blur.
        class _Margins(ctypes.Structure):
            _fields_ = [("cxLeftWidth",    ctypes.c_int),
                        ("cxRightWidth",   ctypes.c_int),
                        ("cyTopHeight",    ctypes.c_int),
                        ("cyBottomHeight", ctypes.c_int)]
        margins = _Margins(0, 0, 0, 1)
        ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(
            ctypes.c_void_p(hwnd), ctypes.byref(margins))
    except Exception:
        # Cosmetic only — never let a missing API or older Windows
        # build take down window creation.
        pass


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
            # overrideredirect() destroys and recreates the native window
            # handle, so the rounded-corners/shadow attributes set at
            # startup were applied to a handle that no longer exists —
            # they have to be re-applied to the new one.
            self._parent.update_idletasks()
            enable_rounded_corners(self._parent)

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


class DarkToplevel(tk.Toplevel):
    """Shared base for dialog windows: dark titlebar with a gold accent
    stripe + gold title (matching CustomTitlebar's style), a thin gold
    rule under the titlebar, and a close button with the same hover
    behavior as the main window.

    Subclasses pack their content into ``self.body``.
    """
    _TB_HEIGHT = 38

    def __init__(self, parent, title="", on_close=None,
                 body_bg=None, padx=0, pady=0,
                 resizable=False, min_width=320, min_height=200):
        super().__init__(parent)
        # Hidden until center_on_parent() positions it correctly — otherwise
        # the window briefly flashes at Tk's default placement (top-left-ish)
        # before jumping to its real spot.
        self.withdraw()
        self.overrideredirect(True)
        body_bg = body_bg or DARK["bg"]
        # The toplevel itself is colored with the border shade; a 1px inset
        # container in the real body color creates a thin outline around
        # the whole window, so it doesn't blend into the app behind it.
        self.configure(bg=DARK["border"])
        self.resizable(resizable, resizable)
        # grab_set() is deferred to center_on_parent() — calling it on a
        # withdrawn window raises "grab failed: window not viewable".

        self._parent       = parent
        self._on_close_cb  = on_close
        self._min_w        = min_width
        self._min_h        = min_height

        container = tk.Frame(self, bg=body_bg)
        container.pack(fill="both", expand=True, padx=1, pady=1)
        self._container = container

        # ── Titlebar ─────────────────────────────────────────────────────
        tb = tk.Frame(container, bg=DARK["bg2"], height=self._TB_HEIGHT)
        tb.pack(fill="x", side="top")
        tb.pack_propagate(False)

        self._title_lbl = tk.Label(
            tb, text=title, bg=DARK["bg2"], fg=DARK["accent"],
            font=("Segoe UI", 9), padx=10)
        self._title_lbl.pack(side="left", fill="y")

        close_lbl = tk.Label(tb, text="✕", bg=DARK["bg2"], fg=DARK["fg2"],
                              font=("Segoe UI", 11), cursor="hand2", width=4)
        close_lbl.pack(side="right", fill="y")
        close_lbl.bind("<Enter>",    lambda _: close_lbl.configure(bg="#3a1010", fg="#c84040"))
        close_lbl.bind("<Leave>",    lambda _: close_lbl.configure(bg=DARK["bg2"], fg=DARK["fg2"]))
        close_lbl.bind("<Button-1>", lambda _: self._close())

        for w in (tb, self._title_lbl):
            w.bind("<ButtonPress-1>", self._drag_start)
            w.bind("<B1-Motion>",     self._drag_move)

        # ── Thin gold accent rule under the titlebar ───────────────────────
        tk.Frame(container, bg=DARK["accent"], height=2).pack(fill="x", side="top")

        # ── Body — subclasses build their content in here ──────────────────
        self.body = tk.Frame(container, bg=body_bg, padx=padx, pady=pady)
        self.body.pack(fill="both", expand=True)

        # ── Resize grip (bottom-right corner) — only when resizable=True ───
        # overrideredirect() removes the native resize border entirely, so
        # without this, a resizable=True window couldn't actually be resized.
        if resizable:
            self._add_resize_grip(container, body_bg)

    def _add_resize_grip(self, container, body_bg):
        # Drawn with Canvas dots rather than a Unicode glyph, so it renders
        # identically regardless of font/emoji support on the target machine.
        size = 14
        grip = tk.Canvas(container, width=size, height=size, bg=body_bg,
                         highlightthickness=0, cursor="size_nw_se")
        grip.place(relx=1.0, rely=1.0, anchor="se", x=-2, y=-2)
        dot = DARK["fg2"]
        for row in range(3):
            for col in range(row + 1):
                x = size - 3 - row * 4
                y = size - 3 - col * 4
                grip.create_oval(x - 1, y - 1, x + 1, y + 1, fill=dot, outline=dot)
        grip.bind("<ButtonPress-1>", self._resize_start)
        grip.bind("<B1-Motion>",     self._resize_move)
        grip.bind("<ButtonRelease-1>", self._resize_end)

    def _resize_start(self, event):
        self._rs_x = event.x_root
        self._rs_y = event.y_root
        self._rs_w = self.winfo_width()
        self._rs_h = self.winfo_height()
        self._rs_pending  = None
        self._rs_scheduled = False

    def _resize_move(self, event):
        new_w = max(self._min_w, self._rs_w + (event.x_root - self._rs_x))
        new_h = max(self._min_h, self._rs_h + (event.y_root - self._rs_y))
        # Coalesce rapid <B1-Motion> events into the latest size only —
        # calling self.geometry() on every single motion event queues up
        # a full reflow (canvas/scrollregion/cards) faster than Tk can
        # process them, which is what causes the second-or-so visible lag
        # on content-heavy windows like Parental Control.
        self._rs_pending = (new_w, new_h)
        if not self._rs_scheduled:
            self._rs_scheduled = True
            self.after(16, self._apply_pending_resize)

    def _apply_pending_resize(self):
        self._rs_scheduled = False
        if self._rs_pending and self.winfo_exists():
            w, h = self._rs_pending
            self._rs_pending = None
            self.geometry(f"{w}x{h}")

    def _resize_end(self, _event=None):
        # Apply the final size immediately on mouse release instead of
        # waiting for the next throttled tick — shaves off the small
        # extra delay that would otherwise linger after the user has
        # already stopped dragging.
        if self._rs_pending and self.winfo_exists():
            w, h = self._rs_pending
            self._rs_pending = None
            self.geometry(f"{w}x{h}")

    def _close(self):
        if self._on_close_cb:
            self._on_close_cb()
        else:
            self.destroy()

    def _drag_start(self, event):
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _drag_move(self, event):
        self.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    def center_on_parent(self, min_w=0, min_h=0):
        # Geometry is computed while still hidden (winfo_reqwidth/reqheight
        # work fine on a withdrawn window), so nothing is visible until the
        # window is already in its final spot — no flash-then-jump.
        center_on_parent(self, self._parent, min_w, min_h)
        self.deiconify()
        self.lift()
        self.update_idletasks()
        enable_rounded_corners(self)
        self.grab_set()


def center_on_parent(win, parent, min_w=0, min_h=0):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    req_w = max(win.winfo_reqwidth(),  min_w)
    req_h = max(win.winfo_reqheight(), min_h)
    w = min(req_w, sw - 40)
    h = min(req_h, sh - 80)
    if parent.winfo_width() <= 1 or parent.winfo_height() <= 1:
        # parent isn't mapped/realized yet (e.g. the password prompt shown
        # at startup, before the main window has a real size/position) —
        # its geometry would be garbage, so center on the screen instead.
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
    else:
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
        win = DarkToplevel(parent, title=title, body_bg=DARK["bg2"],
                            on_close=lambda: (result.__setitem__(0, None), win.destroy()))

        body = tk.Frame(win.body, bg=DARK["bg2"])
        body.pack(padx=20, pady=(18, 10), fill="x")
        tk.Label(body, text=icon, bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI Emoji", 22)).pack(side="left", padx=(0, 14), anchor="n")
        tk.Label(body, text=message, bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI", 10), justify="left",
                 wraplength=360).pack(side="left", anchor="w")

        bf = tk.Frame(win.body, bg=DARK["bg2"])
        bf.pack(pady=(4, 16))
        for label, val in buttons:
            accent = val is True or val == "ok"
            b = make_btn(bf, "", DARK["accent_fg"], label,
                         lambda v=val: (result.__setitem__(0, v), win.destroy()),
                         accent=accent)
            b.pack(side="left", padx=6)

        win.update_idletasks()
        win.center_on_parent()
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
