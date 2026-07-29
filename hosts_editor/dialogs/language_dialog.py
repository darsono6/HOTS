from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QButtonGroup, QRadioButton
from PySide6.QtCore import Qt

from qfluentwidgets import FluentIcon as FIF

from ..constants import DARK
from ..widgets_qt import HOTSDialog, HOTSButton, h_separator
from ..i18n import T, current_lang, LANGUAGES


class LanguageDialog(HOTSDialog):
    def __init__(self, parent=None):
        super().__init__(parent, T("lang_title"), min_width=320, min_height=320)
        self.chosen = None
        self._build()
        self.adjustSize()
        self.center_on_parent()

    def _build(self):
        cl = self.body_layout
        cl.setContentsMargins(28, 24, 28, 16)
        cl.setSpacing(12)

        flags = {"en": "🇬🇧", "pl": "🇵🇱", "fr": "🇫🇷", "de": "🇩🇪", "es": "🇪🇸"}
        self._group = QButtonGroup(self)
        self._radios = {}

        for code, name in LANGUAGES.items():
            rb = QRadioButton(f"{flags.get(code, '')}  {name}")
            rb.setStyleSheet(
                f"QRadioButton {{ color: {DARK['fg']}; background: transparent; spacing: 12px; font-size: 10pt; padding: 4px 0px; }}\n"
                f"QRadioButton::indicator {{ width: 14px; height: 14px; border: 1px solid {DARK['border']}; border-radius: 7px; background: {DARK['indicator_bg']}; }}\n"
                f"QRadioButton::indicator:hover {{ border: 1px solid {DARK['accent']}; }}\n"
                f"QRadioButton::indicator:checked {{ background: transparent; border: 4px solid {DARK['accent']}; }}"
            )
            if code == current_lang():
                rb.setChecked(True)
            self._group.addButton(rb)
            self._radios[rb] = code
            cl.addWidget(rb)

        cl.addStretch()
        cl.addWidget(h_separator())

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = HOTSButton(FIF.ACCEPT, "#ffffff", T("btn_ok"), accent=True)
        ok_btn.fit_to_content()
        ok_btn.clicked.connect(self._apply)
        btn_row.addWidget(ok_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)

    def _apply(self):
        for rb, code in self._radios.items():
            if rb.isChecked():
                self.chosen = code
                break
        self.accept()