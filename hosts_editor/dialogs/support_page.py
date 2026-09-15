import os
import webbrowser

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QIcon

from qfluentwidgets import FluentIcon as FIF

from ..constants import DARK, IS_LIGHT_THEME
from ..widgets_qt import HOTSPage, HOTSDialog, HOTSButton
from ..i18n import T

from ._support_shared import (
    PAYPAL_LINK, PAYPAL_EMAIL, CONTACT_EMAIL, KOFI_LINK, ClickableLabel, _safe_t,
)
from ._support_banner_light import _RetroSupportBannerLight
from ._support_banner_dark import _RetroSupportBannerDark


def _make_support_banner(parent=None):
    banner_cls = _RetroSupportBannerLight if IS_LIGHT_THEME else _RetroSupportBannerDark
    return banner_cls(parent)


class SupportPage(HOTSPage):
    def __init__(self, parent=None):
        super().__init__("supportInterface", FIF.HEART, T("sup_title"), parent)
        self._build()

    def _build(self):
        cl = self.content_layout

        banner = _make_support_banner()
        cl.addWidget(banner)
        cl.addSpacing(16)

        greet = QLabel(_safe_t("sup_greeting", "Hi! I'm Darsono."))
        greet.setWordWrap(True)
        greet.setStyleSheet(f"color: {DARK['fg']}; font-size: 14pt; font-weight: bold; background: transparent;")
        cl.addWidget(greet)
        cl.addSpacing(4)

        msg = QLabel(T("sup_body"))
        msg.setWordWrap(True)
        msg.setStyleSheet(f"color: {DARK['fg']}; font-size: 10pt; line-height: 140%; background: transparent;")
        cl.addWidget(msg)
        cl.addSpacing(16)

        card_row = QHBoxLayout()
        card_row.setSpacing(12)

        kofi_btn = self._make_image_button("support_me_on_kofi_dark.png", height=42, on_click=self._open_kofi)
        kofi_already_wired = kofi_btn is not None
        if kofi_btn is None:
            kofi_btn = HOTSButton(FIF.HEART, "#29abe0", T("sup_btn_kofi"))
        kofi_card = self._make_option_card(
            btn=kofi_btn,
            on_click=None if kofi_already_wired else self._open_kofi,
            sub_widgets=[self._make_sub_label(T("sup_kofi_sub"))],
        )
        card_row.addWidget(kofi_card, 1)

        pay_btn = self._make_image_button("paypal_donate_button.png", height=32, on_click=self._open_paypal)
        pay_already_wired = pay_btn is not None
        if pay_btn is None:
            pay_btn = HOTSButton(FIF.HEART, "#0070ba", T("sup_btn_support"))
        lbl_e = ClickableLabel(PAYPAL_EMAIL)
        lbl_e.setStyleSheet("color: #5599dd; font-size: 9pt; text-decoration: underline; background: transparent;")
        lbl_e.setCursor(Qt.PointingHandCursor)
        lbl_e.clicked.connect(self._copy_paypal_email)
        paypal_card = self._make_option_card(
            btn=pay_btn,
            on_click=None if pay_already_wired else self._open_paypal,
            sub_widgets=[lbl_e, self._make_sub_label(T("sup_paypal_sub"))],
        )
        card_row.addWidget(paypal_card, 1)

        cl.addLayout(card_row)
        cl.addSpacing(12)

        alt_row = QHBoxLayout()
        alt_row.setSpacing(6)
        lbl_alt = QLabel(T("sup_alt_contact"))
        lbl_alt.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent;")
        email_lbl = ClickableLabel(CONTACT_EMAIL)
        email_lbl.setStyleSheet("color: #5599dd; font-size: 8pt; text-decoration: underline; background: transparent;")
        email_lbl.setCursor(Qt.PointingHandCursor)
        email_lbl.clicked.connect(self._copy_email)
        alt_row.addWidget(lbl_alt)
        alt_row.addWidget(email_lbl)
        alt_row.addStretch()
        cl.addLayout(alt_row)
        cl.addStretch()

        footer_txt = QLabel(T("sup_footer"))
        footer_txt.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; font-style: italic; background: transparent;")
        cl.addWidget(footer_txt)

        self._setup_watermark()

    def _find_asset(self, name: str) -> str:
        from ..resource_utils import resource_path
        p = resource_path(name)
        return p if os.path.exists(p) else ""

    def _make_watermark_pixmap(self, path: str, height: int, opacity: float):
        src = QPixmap(path)
        if src.isNull():
            return QPixmap(), QSize(0, 0)

        logical_h = height
        logical_w = max(1, round(src.width() * (logical_h / src.height())))

        render_h = max(1, logical_h * 3)
        scaled = src.scaledToHeight(render_h, Qt.SmoothTransformation)

        faded = QPixmap(scaled.size())
        faded.fill(Qt.transparent)
        painter = QPainter(faded)
        try:
            painter.setOpacity(opacity)
            painter.drawPixmap(0, 0, scaled)
        finally:
            painter.end()
        return faded, QSize(logical_w, logical_h)

    def _setup_watermark(self):
        try:
            path = self._find_asset("logoS.png")
            if not path:
                return
            pix, logical_size = self._make_watermark_pixmap(path, height=25, opacity=0.15)
            if pix.isNull():
                return

            self._watermark_lbl = QLabel(self)
            self._watermark_lbl.setPixmap(pix)
            self._watermark_lbl.setScaledContents(True)
            self._watermark_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
            self._watermark_lbl.setStyleSheet("background: transparent;")
            self._watermark_lbl.setFixedSize(logical_size)
            self._watermark_lbl.lower()
            self._position_watermark()
        except Exception as e:
            print(f"Support watermark setup warning: {e}")

    def _position_watermark(self):
        lbl = getattr(self, "_watermark_lbl", None)
        if not lbl:
            return
        margin = 16
        available_w = self.width() - 2 * margin
        if lbl.width() > max(available_w, 0):
            lbl.hide()
            return
        lbl.show()
        x = self.width() - lbl.width() - margin
        y = self.height() - lbl.height() - margin
        lbl.move(max(x, margin), max(y, margin))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_watermark()

    def _make_sub_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent;")
        return lbl

    def _make_image_button(self, asset_name: str, height: int, on_click):
        path = self._find_asset(asset_name)
        if not path:
            return None
        src = QPixmap(path)
        if src.isNull():
            return None

        w = max(1, round(src.width() * (height / src.height())))
        render_h = max(1, height * 3)
        scaled = src.scaledToHeight(render_h, Qt.SmoothTransformation)

        btn = QPushButton()
        btn.setFlat(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0px; }")
        btn.setIcon(QIcon(scaled))
        btn.setIconSize(QSize(w, height))
        btn.setFixedSize(w, height)
        btn.clicked.connect(on_click)
        return btn

    def _make_option_card(self, btn, on_click, sub_widgets, emoji: str = None, title: str = None):
        card = QFrame()
        card.setObjectName("supportOptionCard")
        card.setStyleSheet(f"""
            QFrame#supportOptionCard {{
                background: {DARK['panel_bg']};
                border-radius: 8px;
                border: 1px solid {DARK['border_soft2']};
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)

        if title:
            title_row = QHBoxLayout()
            title_row.setSpacing(6)
            if emoji:
                lbl_ico = QLabel(emoji)
                lbl_ico.setStyleSheet("font-size: 10pt; background: transparent;")
                title_row.addWidget(lbl_ico)
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet(f"color: {DARK['fg']}; font-size: 11pt; font-weight: bold; background: transparent;")
            title_row.addWidget(lbl_title)
            title_row.addStretch()
            lay.addLayout(title_row)

        if hasattr(btn, "fit_to_content"):
            btn.fit_to_content()
            btn.setMinimumHeight(38)
        if on_click is not None:
            btn.clicked.connect(on_click)
        lay.addWidget(btn)

        for w in sub_widgets:
            lay.addWidget(w)

        lay.addStretch()
        return card

    def _open_paypal(self):
        try:
            webbrowser.open(PAYPAL_LINK)
        except Exception:
            HOTSDialog.error(self, T("sup_title"), T("sup_err_browser", url=PAYPAL_LINK))

    def _open_kofi(self):
        try:
            webbrowser.open(KOFI_LINK)
        except Exception:
            HOTSDialog.error(self, T("sup_title"), T("sup_err_browser", url=KOFI_LINK))

    def _copy_paypal_email(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(PAYPAL_EMAIL)
        HOTSDialog.info(self, T("sup_copied_title"), T("sup_copied_msg"))

    def _copy_email(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(CONTACT_EMAIL)
        HOTSDialog.info(self, T("sup_copied_title"), T("sup_copied_msg"))
