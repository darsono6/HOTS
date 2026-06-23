"""
Parental Control management window and content filters.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk

from ..constants import DARK, load_settings, save_settings
from ..core import is_parental_active, toggle_parental_control
from ..widgets import make_btn, DarkDialog, DarkToplevel, enable_rounded_corners
from ..i18n import T
from ..dns_utils import (
    is_cf_family_active,
    enable_cf_family_dns,
    disable_cf_family_dns,
)
from ..core_antispy import AntiSpyManager


class _Tooltip:
    """Simple dark-themed tooltip that follows the widget it's attached to."""
    _WRAP = 340

    def __init__(self, widget, text: str):
        self._widget = widget
        self._text   = text
        self._tip    = None
        widget.bind("<Enter>",  self._show)
        widget.bind("<Leave>",  self._hide)
        widget.bind("<Destroy>", lambda _: self._hide())

    def _show(self, _event=None):
        if self._tip:
            return
        x = self._widget.winfo_rootx() + self._widget.winfo_width() // 2
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 6

        self._tip = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        # Outer toplevel is the border color; a 1px-inset inner frame in
        # the real background color creates the same thin outline used
        # by every other window in the app (DarkToplevel).
        tw.configure(bg=DARK["border"])

        container = tk.Frame(tw, bg="#2e2e2e")
        container.pack(padx=1, pady=1)

        tk.Label(
            container, text=self._text,
            bg="#2e2e2e", fg=DARK["fg"],
            font=("Segoe UI", 9),
            justify="left",
            wraplength=self._WRAP,
            padx=10, pady=8,
            relief="flat",
        ).pack()

        tw.update_idletasks()
        enable_rounded_corners(tw)

    def _hide(self, _event=None):
        if self._tip:
            self._tip.destroy()
            self._tip = None


class _BlinkingIcon:
    """
    Makes a label blink between two colors until it's clicked once.
    The acknowledgment is persisted to settings.json (not just kept in
    memory), so once dismissed it stays dismissed across app restarts —
    not only for the current session.
    """
    _INTERVAL_MS = 600
    _SETTINGS_KEY = "parental_warning_dismissed"
    _acknowledged = None  # lazily loaded from disk on first use, then cached

    def __init__(self, label: tk.Label, active_color: str, idle_color: str):
        self._label  = label
        self._active = active_color
        self._idle   = idle_color
        self._job    = None
        self._on     = True

        if _BlinkingIcon._acknowledged is None:
            try:
                _BlinkingIcon._acknowledged = bool(load_settings().get(self._SETTINGS_KEY, False))
            except Exception:
                _BlinkingIcon._acknowledged = False

        if _BlinkingIcon._acknowledged:
            label.configure(fg=idle_color)
            return

        label.bind("<Button-1>", self._acknowledge, add="+")
        self._tick()

    def _tick(self):
        if _BlinkingIcon._acknowledged:
            self._label.configure(fg=self._idle)
            return
        self._label.configure(fg=self._active if self._on else self._idle)
        self._on  = not self._on
        self._job = self._label.after(self._INTERVAL_MS, self._tick)

    def _acknowledge(self, _event=None):
        _BlinkingIcon._acknowledged = True
        if self._job:
            self._label.after_cancel(self._job)
            self._job = None
        self._label.configure(fg=self._idle)
        try:
            # Re-read fresh from disk before writing — same precaution as
            # ParentalDialog's own size-saving, so this can't clobber (or
            # be clobbered by) keys other windows manage.
            saved = load_settings()
            saved[self._SETTINGS_KEY] = True
            save_settings(saved)
        except Exception:
            pass


def _get_blocklists_dir() -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "blocklists")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "blocklists")


CATEGORIES = [
    {"label_key": "par_cat_xxx",       "icon": "🔞", "color": "#cc2222", "file": "xxx.txt"},
    {"label_key": "par_cat_twitter",   "icon": "🐦", "color": "#1DA1F2", "file": "twitter.txt"},
    {"label_key": "par_cat_instagram", "icon": "📸", "color": "#E1306C", "file": "instagram.txt"},
    {"label_key": "par_cat_youtube",   "icon": "▶",  "color": "#FF0000", "file": "youtube.txt"},
    {"label_key": "par_cat_facebook",  "icon": "👤", "color": "#1877F2", "file": "facebook.txt"},
    {"label_key": "par_cat_whatsapp",  "icon": "💬", "color": "#25D366", "file": "whatsapp.txt"},
    {"label_key": "par_cat_tiktok",    "icon": "🎵", "color": "#ff2d55", "file": "tiktok.txt"},
    {"label_key": "par_cat_twitch",    "icon": "🎮", "color": "#9146FF", "file": "twitch.txt"},
    {"label_key": "par_cat_snapchat",  "icon": "👻", "color": "#FFFC00", "file": "snapchat.txt"},
    {"label_key": "par_cat_pinterest", "icon": "📌", "color": "#E60023", "file": "pinterest.txt"},
    {"label_key": "par_cat_reddit",    "icon": "🤖", "color": "#FF4500", "file": "reddit.txt"},
    {"label_key": "par_cat_games",     "icon": "🕹️", "color": "#7b2d8b", "file": "games.txt"},
    {"label_key": "par_cat_antispy",   "icon": "🛡", "color": "#0078D4", "file": "antispy.txt"},
    {"label_key": "par_cat_torrent",   "icon": "⛔", "color": "#aaaaaa", "file": "torrent.txt"},
]

_CF_ACCENT = "#f5a623"


class ParentalDialog(DarkToplevel):
    def __init__(self, parent):
        super().__init__(parent, title=T("par_title"), body_bg=DARK["bg"],
                          resizable=False, min_width=540, min_height=440,
                          on_close=self._on_close)
        self.resizable(False, True)
        self.parent = parent
        self._blocklists_dir = _get_blocklists_dir()

        self._build_ui()

        # Vertical-only resize grip on _container (same placement as DarkToplevel)
        _size = 14
        _grip = tk.Canvas(self._container, width=_size, height=_size, bg=DARK["bg"],
                          highlightthickness=0, cursor="size_ns")
        _grip.place(relx=1.0, rely=1.0, anchor="se", x=-2, y=-2)
        _dot = DARK["fg2"]
        for _row in range(3):
            for _col in range(_row + 1):
                _x = _size - 3 - _row * 4
                _y = _size - 3 - _col * 4
                _grip.create_oval(_x-1, _y-1, _x+1, _y+1, fill=_dot, outline=_dot)
        _grip.bind("<ButtonPress-1>",   self._vresize_start)
        _grip.bind("<B1-Motion>",       self._vresize_move)
        _grip.bind("<ButtonRelease-1>", self._vresize_end)

        # The category list lives inside a Canvas (for scrolling), which
        # breaks Tk's normal width propagation — a Canvas's own reqwidth
        # is independent of what its scrolled content actually needs. So
        # the window's natural reqwidth can't be trusted on its own; the
        # real required width has to come from the cards themselves,
        # otherwise longer translations (e.g. French button labels) or a
        # different Windows DPI scale could get clipped.
        self._cards_frame.update_idletasks()
        content_w = self._cards_frame.winfo_reqwidth() + 50  # canvas padding + scrollbar
        min_w = max(540, content_w)

        saved_h = load_settings().get("par_dialog_height", 440)
        saved_h = max(440, int(saved_h))
        self.center_on_parent(min_w=min_w, min_h=saved_h)
        self.wait_window()

    def _vresize_start(self, event):
        self._vrs_y = event.y_root
        self._vrs_h = self.winfo_height()
        self._vrs_pending = None
        self._vrs_scheduled = False

    def _vresize_move(self, event):
        new_h = max(440, self._vrs_h + (event.y_root - self._vrs_y))
        self._vrs_pending = new_h
        if not self._vrs_scheduled:
            self._vrs_scheduled = True
            self.after(16, self._vresize_apply)

    def _vresize_apply(self):
        self._vrs_scheduled = False
        if self._vrs_pending and self.winfo_exists():
            h = self._vrs_pending
            self._vrs_pending = None
            self.geometry(f"{self.winfo_width()}x{h}")

    def _vresize_end(self, _event=None):
        if self._vrs_pending and self.winfo_exists():
            h = self._vrs_pending
            self._vrs_pending = None
            self.geometry(f"{self.winfo_width()}x{h}")

    def _on_close(self):
        try:
            h = self.winfo_height()
            if h > 0:
                saved = load_settings()
                saved["par_dialog_height"] = h
                save_settings(saved)
        except Exception:
            pass
        self.destroy()

    def _build_ui(self):
        header = tk.Frame(self.body, bg=DARK["bg2"], padx=20, pady=14,
                          highlightthickness=1, highlightbackground=DARK["border"])
        header.pack(fill="x")

        title_row = tk.Frame(header, bg=DARK["bg2"])
        title_row.pack(anchor="w", fill="x")

        tk.Label(title_row, text=T("par_header"),
                 bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI", 12, "bold")).pack(side="left")

        _warn_icon = tk.Label(
            title_row, text="⚠️",
            bg=DARK["bg2"], fg="#f5a623",
            font=("Segoe UI Emoji", 11),
            cursor="question_arrow",
            padx=6,
        )
        _warn_icon.pack(side="left", padx=(8, 0))

        _Tooltip(_warn_icon, T("par_limitations_tooltip"))
        _BlinkingIcon(_warn_icon, active_color="#f5a623", idle_color="#6a4a18")

        tk.Label(header, text=T("par_subheader"),
                 bg=DARK["bg2"], fg="#8a8a8a",
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        canvas_frame = tk.Frame(self.body, bg=DARK["bg"])
        canvas_frame.pack(fill="both", expand=True, padx=12, pady=10)

        canvas = tk.Canvas(canvas_frame, bg=DARK["bg"], highlightthickness=0, bd=0)
        vsb = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._cards_frame = tk.Frame(canvas, bg=DARK["bg"])
        window_id = canvas.create_window((0, 0), window=self._cards_frame, anchor="nw")

        def _on_frame_configure(_):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(window_id, width=event.width)

        self._cards_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        self._category_states = {}
        for cat in CATEGORIES:
            self._build_card(self._cards_frame, cat)
            if cat["file"] == "xxx.txt":
                self._build_cf_dns_card(self._cards_frame)

        footer = tk.Frame(self.body, bg=DARK["bg2"], padx=12, pady=10,
                          highlightthickness=1, highlightbackground=DARK["border"])
        footer.pack(fill="x", side="bottom")

        make_btn(footer, "✖", "#e05050", T("par_btn_close"), self._on_close).pack(side="right")
        tk.Label(footer, text=T("par_blocklists_path", path=self._blocklists_dir),
                 bg=DARK["bg2"], fg="#555555",
                 font=("Segoe UI", 8)).pack(side="left")

    def _build_cf_dns_card(self, parent):
        active = is_cf_family_active()
        card = tk.Frame(parent, bg=DARK["bg2"],
                        highlightthickness=1, highlightbackground=DARK["border"])
        card.pack(fill="x", pady=3)

        tk.Frame(card, bg=_CF_ACCENT, width=4).pack(side="left", fill="y")

        info = tk.Frame(card, bg=DARK["bg2"], padx=12, pady=10)
        info.pack(side="left", fill="both", expand=True)

        top_row = tk.Frame(info, bg=DARK["bg2"])
        top_row.pack(anchor="w")

        tk.Label(top_row, text="🌐",
                 bg=DARK["bg2"], fg=_CF_ACCENT,
                 font=("Segoe UI Emoji", 14)).pack(side="left", padx=(0, 8))
        tk.Label(top_row, text=T("par_cf_title"),
                 bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        tk.Label(info, text=T("par_cf_desc"),
                 bg=DARK["bg2"], fg="#555555",
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 0))

        btn_area = tk.Frame(card, bg=DARK["bg2"], padx=12)
        btn_area.pack(side="right", fill="y")

        btn_row = tk.Frame(btn_area, bg=DARK["bg2"])
        btn_row.pack(expand=True)

        info_icon = tk.Label(
            btn_row, text="?",
            bg=DARK["bg2"], fg=DARK.get("red", "#e05050"),
            font=("Segoe UI", 12, "bold"),
            cursor="question_arrow",
        )
        info_icon.pack(side="left", padx=(0, 8))
        _Tooltip(info_icon, T("par_cf_tooltip"))

        self._cf_state = {"active": active, "btn": None}
        btn_color = DARK.get("red", "#e05050") if active else "#43b581"
        btn_label = T("par_cf_btn_disable") if active else T("par_cf_btn_enable")

        btn = make_btn(btn_row, "⏻", btn_color, btn_label,
                       self._toggle_cf_dns, accent=True)
        btn._base_bg = btn_color
        for w in [btn] + list(btn.winfo_children()):
            w.configure(bg=btn_color)

        btn.pack(side="left")
        self._cf_state["btn"] = btn

    def _update_cf_btn(self):
        active = self._cf_state["active"]
        btn    = self._cf_state["btn"]
        color  = DARK.get("red", "#e05050") if active else "#43b581"
        label  = T("par_cf_btn_disable") if active else T("par_cf_btn_enable")

        btn._base_bg = color
        for w in [btn] + list(btn.winfo_children()):
            w.configure(bg=color)
        children = btn.winfo_children()
        if len(children) >= 2:
            children[1].configure(text=label, fg=DARK["accent_fg"])

    def _toggle_cf_dns(self):
        currently_active = self._cf_state["active"]
        if not currently_active:
            xxx_state = self._category_states.get("xxx.txt")
            if xxx_state and xxx_state["active"]:
                xxx_path = xxx_state["path"]
                ok = toggle_parental_control(False, xxx_path, tag_suffix="xxx.txt")
                if ok:
                    xxx_state["active"] = False
                    self._update_btn(xxx_state)
                    if hasattr(self.parent, "_reload"):
                        self.parent._reload()
                else:
                    DarkDialog.error(self, T("par_cf_title"), T("par_err_hosts_msg"))
                    return

            ok, failed = enable_cf_family_dns()
            if ok:
                self._cf_state["active"] = True
                self._update_cf_btn()
                msg = T("par_cf_on_ok")
                if failed:
                    msg += "\n" + T("par_cf_partial_fail", ifaces=", ".join(failed))
                DarkDialog.info(self, T("par_cf_title"), msg)
            else:
                DarkDialog.error(self, T("par_cf_title"), T("par_cf_on_fail"))
        else:
            ok, failed = disable_cf_family_dns()
            if ok:
                self._cf_state["active"] = False
                self._update_cf_btn()
                DarkDialog.info(self, T("par_cf_title"), T("par_cf_off_ok"))
            else:
                err_msg = T("par_cf_off_fail")
                if failed:
                    err_msg += "\n" + T("par_cf_partial_fail", ifaces=", ".join(failed))
                DarkDialog.error(self, T("par_cf_title"), err_msg)

    def _build_card(self, parent, cat):
        list_path = os.path.join(self._blocklists_dir, cat["file"])
        if cat["file"] == "antispy.txt":
            # AntiSpy's real protection is services/registry/firewall
            # (AntiSpyManager) — a hosts-file blocklist for it is optional
            # and, even when present, isn't a reliable signal of whether
            # the actual protection is on (e.g. it survives an unrelated
            # hosts restore). Status has to come from AntiSpyManager.
            active = AntiSpyManager.is_active()
        else:
            active = is_parental_active(tag_suffix=cat["file"])
        file_ok   = os.path.exists(list_path)

        card = tk.Frame(parent, bg=DARK["bg2"],
                        highlightthickness=1, highlightbackground=DARK["border"])
        card.pack(fill="x", pady=3)

        tk.Frame(card, bg=cat["color"], width=4).pack(side="left", fill="y")

        info = tk.Frame(card, bg=DARK["bg2"], padx=12, pady=10)
        info.pack(side="left", fill="both", expand=True)

        top_row = tk.Frame(info, bg=DARK["bg2"])
        top_row.pack(anchor="w")

        tk.Label(top_row, text=cat["icon"],
                 bg=DARK["bg2"], fg=cat["color"],
                 font=("Segoe UI Emoji", 14)).pack(side="left", padx=(0, 8))
        tk.Label(top_row, text=T(cat["label_key"]),
                 bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        # Status text for Windows AntiSpy used to be a static "ready"
        # label that never reflected real state — removed now that the
        # tooltip next to the toggle button explains what enable/disable
        # actually do.
        if cat["file"] == "antispy.txt":
            file_txt = None
            is_disabled_state = False
        else:
            if file_ok:
                file_txt = T("par_file_ok", file=cat["file"])
                file_fg  = "#555555"
                is_disabled_state = False
            else:
                file_txt = T("par_file_missing", file=cat["file"])
                file_fg  = DARK.get("red", "#e05050")
                is_disabled_state = not active

        if file_txt:
            tk.Label(info, text=file_txt,
                     bg=DARK["bg2"], fg=file_fg,
                     font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 0))

        btn_area = tk.Frame(card, bg=DARK["bg2"], padx=12)
        btn_area.pack(side="right", fill="y")

        btn_row = tk.Frame(btn_area, bg=DARK["bg2"])
        btn_row.pack(expand=True)

        if cat["file"] == "antispy.txt":
            info_icon = tk.Label(
                btn_row, text="?",
                bg=DARK["bg2"], fg=DARK.get("red", "#e05050"),
                font=("Segoe UI", 12, "bold"),
                cursor="question_arrow",
            )
            info_icon.pack(side="left", padx=(0, 8))
            _Tooltip(info_icon, T("par_antispy_tooltip"))

        state = {
            "active": active,
            "cat":    cat,
            "path":   list_path,
            "btn":    None,
        }
        self._category_states[cat["file"]] = state

        btn_color = DARK.get("red", "#e05050") if active else "#43b581"
        btn_label = T("par_btn_disable") if active else T("par_btn_enable")

        btn = make_btn(btn_row, "⏻", btn_color, btn_label,
                       lambda s=state: self._toggle(s), accent=True)
        btn._base_bg = btn_color
        for w in [btn] + list(btn.winfo_children()):
            w.configure(bg=btn_color)

        btn.pack(side="left")
        state["btn"] = btn

        if is_disabled_state:
            self._set_btn_disabled(btn)

    def _set_btn_disabled(self, btn):
        disabled_bg = DARK["bg3"]
        btn._base_bg = disabled_bg
        for w in [btn] + list(btn.winfo_children()):
            w.configure(bg=disabled_bg)
        children = btn.winfo_children()
        if len(children) >= 2:
            children[1].configure(text=T("par_btn_no_file"), fg="#666666")

    def _set_btn_working(self, btn):
        working_bg = DARK["bg3"]
        btn._base_bg = working_bg
        for w in [btn] + list(btn.winfo_children()):
            w.configure(bg=working_bg)
        children = btn.winfo_children()
        if len(children) >= 2:
            children[1].configure(text=T("par_btn_working"), fg="#888888")

    def _update_btn(self, state):
        btn    = state["btn"]
        active = state["active"]
        color  = DARK.get("red", "#e05050") if active else "#43b581"
        label  = T("par_btn_disable") if active else T("par_btn_enable")

        btn._base_bg = color
        for w in [btn] + list(btn.winfo_children()):
            w.configure(bg=color)
        children = btn.winfo_children()
        if len(children) >= 2:
            children[1].configure(text=label, fg=DARK["accent_fg"])

    def _toggle(self, state):
        cat       = state["cat"]
        list_path = state["path"]
        target    = not state["active"]

        if target and not os.path.exists(list_path) and cat["file"] != "antispy.txt":
            DarkDialog.error(self, T("par_err_no_file_title"),
                             T("par_err_no_file_msg", path=list_path, file=cat["file"]))
            return

        if cat["file"] == "antispy.txt":
            if getattr(self, "_antispy_busy", False):
                return
            self._toggle_antispy_async(state, target)
            return

        self._apply_toggle(state, target)

    def _toggle_antispy_async(self, state, target):
        """
        Runs the AntiSpy engine (services/registry/firewall) on a
        background thread, since the underlying sc/net/netsh calls can
        take a few seconds and would otherwise freeze the Tkinter UI.
        """
        self._antispy_busy = True
        self._set_btn_working(state["btn"])

        def worker():
            ok = AntiSpyManager.enable_antispy() if target else AntiSpyManager.disable_antispy()
            try:
                self.after(0, lambda: self._on_antispy_done(state, target, ok))
            except tk.TclError:
                pass  # dialog was closed before the engine finished

        threading.Thread(target=worker, daemon=True).start()

    def _on_antispy_done(self, state, target, antispy_ok):
        self._antispy_busy = False

        if not antispy_ok:
            # Do not touch the hosts file or mark the category as active,
            # so the displayed status always matches what actually
            # happened on the system (e.g. missing admin rights).
            self._update_btn(state)
            DarkDialog.error(self, T("par_antispy_err_title"), T("par_antispy_err_msg"))
            return

        self._apply_toggle(state, target)

    def _apply_toggle(self, state, target):
        cat       = state["cat"]
        list_path = state["path"]

        # If a physical file exists, also update the hosts file.
        # (For antispy.txt this is optional — AntiSpyManager's real
        # protection from is_active()'s point of view doesn't depend on
        # it — but if a blocklist *is* present alongside it, its domains
        # should still be written/removed the normal way.)
        if os.path.exists(list_path) or cat["file"] == "antispy.txt":
            success = toggle_parental_control(target, list_path, tag_suffix=cat["file"])
        else:
            success = True

        if success:
            state["active"] = target
            self._update_btn(state)
            if hasattr(self.parent, "_reload"):
                self.parent._reload()
            msg_key = "par_success_on" if target else "par_success_off"
            DarkDialog.info(self, T("par_success_title"),
                            T(msg_key, label=T(cat["label_key"])))
        else:
            self._update_btn(state)
            DarkDialog.error(self, T("par_err_hosts_title"), T("par_err_hosts_msg"))