"""
Project support / donation window for HOTS.
File: dialogs/support_dialog.py
"""

import os
import sys
import tkinter as tk
import webbrowser

from ..constants import DARK
from ..widgets import make_btn, DarkDialog, DarkToplevel
from ..i18n import T

PAYPAL_LINK   = "https://paypal.me/darsonodark"
PAYPAL_EMAIL  = "darsono.dark@gmail.com"
CONTACT_EMAIL = "hots.support@gmail.com"

# Path to the banner image — resolved relative to this file (also works in EXE)
def _banner_path() -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "assets", "banner.png")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "banner.png")


class SupportDialog(DarkToplevel):
    def __init__(self, parent):
        super().__init__(parent, title=T("sup_title"), body_bg=DARK["bg"],
                          min_width=480, min_height=380)

        self._build_ui()

        self.center_on_parent(min_w=480, min_h=380)
        self.wait_window()

    def _build_ui(self):
        # ── Banner image ─────────────────────────────────────────────────
        BANNER_W = 480
        BANNER_H = 180

        banner_frame = tk.Frame(self.body, bg=DARK["bg"], width=BANNER_W, height=BANNER_H)
        banner_frame.pack(fill="x")
        banner_frame.pack_propagate(False)

        try:
            from PIL import Image, ImageTk
            img = Image.open(_banner_path())
            img = img.resize((BANNER_W, BANNER_H), Image.LANCZOS)
            self._banner_img = ImageTk.PhotoImage(img)
            tk.Label(banner_frame, image=self._banner_img,
                     bg=DARK["bg"], bd=0).pack(fill="both", expand=True)
        except Exception:
            # Fallback: dark bar with gold text (if PIL is unavailable or file is missing)
            fb = tk.Frame(banner_frame, bg=DARK["accent"], height=BANNER_H)
            fb.pack(fill="both", expand=True)
            tk.Label(fb, text="HOTS", bg=DARK["accent"], fg="#d4a017",
                     font=("Segoe UI", 32, "bold")).pack(expand=True)

        # ── Content ──────────────────────────────────────────────────────
        body = tk.Frame(self.body, bg=DARK["bg"], padx=30, pady=20)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=T("sup_greeting"),
                 bg=DARK["bg"], fg=DARK["fg"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")

        tk.Label(body, text=T("sup_body"),
                 bg=DARK["bg"], fg="#aaaaaa",
                 font=("Segoe UI", 9), justify="left").pack(anchor="w", pady=(8, 20))

        # ── PayPal card ──────────────────────────────────────────────────
        card = tk.Frame(body, bg=DARK["bg2"],
                        highlightthickness=1, highlightbackground=DARK["border"])
        card.pack(fill="x", pady=(0, 16))

        card_inner = tk.Frame(card, bg=DARK["bg2"], padx=16, pady=14)
        card_inner.pack(fill="x")

        left = tk.Frame(card_inner, bg=DARK["bg2"])
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="💳  PayPal",
                 bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(left, text=PAYPAL_EMAIL,
                 bg=DARK["bg2"], fg="#5599dd",
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))
        tk.Label(left, text=T("sup_paypal_sub"),
                 bg=DARK["bg2"], fg="#555555",
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 0))

        make_btn(card_inner, "❤", "#e05050", T("sup_btn_support"),
                 self._open_paypal, accent=True).pack(side="right", padx=(12, 0))

        # ── Alternative — email ──────────────────────────────────────────
        alt = tk.Frame(body, bg=DARK["bg"])
        alt.pack(fill="x")

        tk.Label(alt, text=T("sup_alt_contact"),
                 bg=DARK["bg"], fg="#555555",
                 font=("Segoe UI", 8)).pack(side="left")

        email_lbl = tk.Label(alt, text=CONTACT_EMAIL,
                              bg=DARK["bg"], fg="#5599dd",
                              font=("Segoe UI", 8, "underline"),
                              cursor="hand2")
        email_lbl.pack(side="left", padx=(5, 0))
        email_lbl.bind("<Button-1>", lambda _: self._copy_email())

        # ── Footer ───────────────────────────────────────────────────────
        footer = tk.Frame(self.body, bg=DARK["bg2"], padx=16, pady=10,
                          highlightthickness=1, highlightbackground=DARK["border"])
        footer.pack(fill="x", side="bottom")

        tk.Label(footer, text=T("sup_footer"),
                 bg=DARK["bg2"], fg="#555555",
                 font=("Segoe UI", 8, "italic")).pack(side="left")

        make_btn(footer, "✖", "#e05050", T("sup_btn_close"),
                 self.destroy).pack(side="right")

    def _open_paypal(self):
        try:
            webbrowser.open(PAYPAL_LINK)
        except Exception:
            DarkDialog.error(self, "Error",
                             T("sup_err_browser", url=PAYPAL_LINK))

    def _copy_email(self):
        self.clipboard_clear()
        self.clipboard_append(CONTACT_EMAIL)
        DarkDialog.info(self, T("sup_copied_title"), T("sup_copied_msg"))
