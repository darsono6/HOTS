from PySide6.QtWidgets import QHBoxLayout, QGridLayout, QButtonGroup

from ..icons import FIF
from ..widgets_qt import HOTSDialog, HOTSButton, h_separator, HOTSRadio
from ..i18n import T, current_lang, LANGUAGES


class LanguageDialog(HOTSDialog):
    def __init__(self, parent=None):
        super().__init__(parent, T("lang_title"), min_width=380, min_height=220)
        self.chosen = None
        self._build()
        self.adjustSize()
        self.center_on_parent()

    def _build(self):
        cl = self.body_layout
        cl.setContentsMargins(28, 24, 28, 16)
        cl.setSpacing(12)

        flags = {"en": "🇬🇧", "pl": "🇵🇱", "fr": "🇫🇷", "de": "🇩🇪", "es": "🇪🇸", "pt": "🇵🇹", "ru": "🇷🇺"}
        self._group = QButtonGroup(self)
        self._radios = {}

        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(8)
        cols = 2
        for i, (code, name) in enumerate(LANGUAGES.items()):
            rb = HOTSRadio(f"{flags.get(code, '')}  {name}", pad_v=4)
            if code == current_lang():
                rb.setChecked(True)
            self._group.addButton(rb)
            self._radios[rb] = code
            grid.addWidget(rb, i // cols, i % cols)

        cl.addLayout(grid)

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