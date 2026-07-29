from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel

from ..i18n import T

PAYPAL_LINK   = "https://paypal.me/darsonodark"
PAYPAL_EMAIL  = "darsono.dark@gmail.com"
CONTACT_EMAIL = "hots.support@gmail.com"


def _safe_t(key: str, fallback: str) -> str:
    try:
        val = T(key)
        if not val or val == key:
            return fallback
        return val
    except Exception:
        return fallback


class ClickableLabel(QLabel):
    clicked = Signal()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
