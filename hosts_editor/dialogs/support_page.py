import webbrowser

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from qfluentwidgets import FluentIcon as FIF

from ..constants import DARK, IS_LIGHT_THEME
from ..widgets_qt import HOTSPage, HOTSDialog, HOTSButton
from ..i18n import T

from ._support_shared import (
    PAYPAL_LINK, PAYPAL_EMAIL, CONTACT_EMAIL, ClickableLabel, _safe_t,
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

        card = QFrame()
        card.setObjectName("paypalCard")
        card.setStyleSheet(f"""
            QFrame#paypalCard {{
                background: {DARK['panel_bg']};
                border-radius: 8px;
                border: 1px solid {DARK['border_soft2']};
            }}
        """)
        card_lay = QHBoxLayout(card)
        card_lay.setContentsMargins(14, 12, 14, 12)
        card_lay.setSpacing(14)

        pay_btn = HOTSButton(FIF.HEART, "#ffffff", T("sup_btn_support"), accent=True)
        pay_btn.fit_to_content()
        pay_btn.setMinimumHeight(38)
        pay_btn.clicked.connect(self._open_paypal)
        card_lay.addWidget(pay_btn)

        mail_info = QVBoxLayout()
        mail_info.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        lbl_ico = QLabel("💳")
        lbl_ico.setStyleSheet("font-size: 10pt; background: transparent;")
        title_row.addWidget(lbl_ico)
        lbl_title = QLabel("PayPal")
        lbl_title.setStyleSheet(f"color: {DARK['fg']}; font-size: 11pt; font-weight: bold; background: transparent;")
        title_row.addWidget(lbl_title)
        title_row.addStretch()
        mail_info.addLayout(title_row)

        lbl_e = ClickableLabel(PAYPAL_EMAIL)
        lbl_e.setStyleSheet("color: #5599dd; font-size: 9pt; text-decoration: underline; background: transparent;")
        lbl_e.setCursor(Qt.PointingHandCursor)
        lbl_e.clicked.connect(self._copy_paypal_email)
        mail_info.addWidget(lbl_e)

        lbl_p = QLabel(T("sup_paypal_sub"))
        lbl_p.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent;")
        mail_info.addWidget(lbl_p)

        card_lay.addLayout(mail_info)
        card_lay.addStretch()
        cl.addWidget(card)
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

    def _open_paypal(self):
        try:
            webbrowser.open(PAYPAL_LINK)
        except Exception:
            HOTSDialog.error(self, T("sup_title"), T("sup_err_browser", url=PAYPAL_LINK))

    def _copy_paypal_email(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(PAYPAL_EMAIL)
        HOTSDialog.info(self, T("sup_copied_title"), T("sup_copied_msg"))

    def _copy_email(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(CONTACT_EMAIL)
        HOTSDialog.info(self, T("sup_copied_title"), T("sup_copied_msg"))
