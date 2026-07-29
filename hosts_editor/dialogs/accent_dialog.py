from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QButtonGroup, QPushButton, QRadioButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from qfluentwidgets import FluentIcon as FIF, IconWidget

from ..constants import DARK, ACCENT_PRESETS_DARK, ACCENT_PRESETS_LIGHT, hex_to_rgb
from ..widgets_qt import HOTSDialog, HOTSButton, h_separator
from ..i18n import T


class _AccentRow(QFrame):

    def __init__(self, dot: QRadioButton, tint_rgb: tuple, parent=None):
        super().__init__(parent)
        self._dot = dot
        self._tint_rgb = tint_rgb
        self.setCursor(Qt.PointingHandCursor)
        self._restyle()

    def _restyle(self):
        r, g, b = self._tint_rgb
        checked = self._dot.isChecked()
        bg = f"rgba({r},{g},{b},0.14)" if checked else "transparent"
        self.setStyleSheet(f"QFrame {{ background-color: {bg}; border: none; border-radius: 8px; }}")

    def enterEvent(self, event):
        if not self._dot.isChecked():
            r, g, b = self._tint_rgb
            self.setStyleSheet(f"QFrame {{ background-color: rgba({r},{g},{b},0.07); border: none; border-radius: 8px; }}")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._restyle()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._dot.setChecked(True)
        super().mousePressEvent(event)


class AccentColorDialog(HOTSDialog):
    _LABEL_KEYS = {
        "gold":  "acc_gold",
        "red":   "acc_red",
        "green": "acc_green",
        "blue":  "acc_blue",
    }

    def __init__(self, parent=None, current_accent: str = "gold", current_theme: str = "dark"):
        super().__init__(parent, T("app_title"), min_width=380, min_height=300)
        self.chosen_accent = current_accent
        self.chosen_theme = current_theme
        self._current_accent = current_accent
        self._current_theme = current_theme
        self._theme_buttons = {}
        self._accent_buttons = {}
        self._build()
        self.adjustSize()
        self.center_on_parent()

    def _build(self):
        cl = self.body_layout
        cl.setContentsMargins(28, 24, 28, 20)
        cl.setSpacing(14)

        theme_lbl = QLabel(T("app_theme_label"))
        theme_lbl.setStyleSheet(f"color: {DARK['fg']}; font-size: 10pt; font-weight: 600; background: transparent; border: none;")
        cl.addWidget(theme_lbl)

        theme_track = QFrame()
        theme_track.setStyleSheet(
            f"QFrame {{ background-color: {DARK['btn_bg']}; border: 1px solid {DARK['border']}; "
            f"border-radius: 10px; }}"
        )
        theme_row = QHBoxLayout(theme_track)
        theme_row.setContentsMargins(3, 3, 3, 3)
        theme_row.setSpacing(3)

        for key, label_key, icon_fif in (
            ("dark", "app_theme_dark", FIF.QUIET_HOURS),
            ("light", "app_theme_light", FIF.BRIGHTNESS),
        ):
            btn = self._make_theme_button(icon_fif, T(label_key), key)
            self._theme_buttons[btn]["key"] = key
            theme_row.addWidget(btn, 1)

        cl.addWidget(theme_track)
        cl.addSpacing(4)
        cl.addWidget(h_separator())
        cl.addSpacing(4)

        desc = QLabel(T("acc_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent; border: none;")
        cl.addWidget(desc)

        self._swatch_card = QFrame()
        self._swatch_card.setStyleSheet(
            f"QFrame {{ background-color: {DARK['btn_bg']}; border: 1px solid {DARK['border']}; "
            f"border-radius: 10px; }}"
        )
        self._swatch_layout = QVBoxLayout(self._swatch_card)
        self._swatch_layout.setContentsMargins(8, 8, 8, 8)
        self._swatch_layout.setSpacing(2)
        cl.addWidget(self._swatch_card)
        self._rebuild_swatches(self._current_theme, keep_selection=True)

        cl.addStretch()
        cl.addWidget(h_separator())

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 12, 0, 0)
        btn_row.addStretch()
        ok_btn = HOTSButton(FIF.ACCEPT, "#ffffff", T("btn_ok"), accent=True)
        ok_btn.fit_to_content()
        ok_btn.clicked.connect(self._apply)
        btn_row.addWidget(ok_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)

    def _make_theme_button(self, icon_fif, label_text: str, key: str) -> QPushButton:
        btn = QPushButton()
        btn.setCheckable(True)
        btn.setFixedHeight(36)
        btn.setCursor(Qt.PointingHandCursor)

        lay = QHBoxLayout(btn)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(8)

        ico = IconWidget(icon_fif)
        ico.setFixedSize(15, 15)
        ico.setAttribute(Qt.WA_TransparentForMouseEvents)
        lay.addWidget(ico)

        lbl = QLabel(label_text)
        lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        lay.addWidget(lbl)
        lay.addStretch()

        self._theme_buttons[btn] = {"key": key, "icon_fif": icon_fif, "icon_widget": ico, "label": lbl}
        btn.setChecked(key == self._current_theme)
        self._style_theme_button(btn)
        btn.clicked.connect(lambda _checked=False, k=key: self._select_theme(k))
        return btn

    def _style_theme_button(self, btn: QPushButton):
        info = self._theme_buttons[btn]
        checked = btn.isChecked()
        if checked:
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {DARK['accent']}; border: none; border-radius: 8px; }}"
            )
            info["label"].setStyleSheet(
                "color: #ffffff; font-size: 9.5pt; font-weight: 600; background: transparent; border: none;"
            )
            info["icon_widget"].setIcon(info["icon_fif"].icon(color=QColor("#ffffff")))
        else:
            btn.setStyleSheet(
                f"QPushButton {{ background-color: transparent; border: none; border-radius: 8px; }}"
                f"QPushButton:hover {{ background-color: {DARK['btn_hover']}; }}"
            )
            info["label"].setStyleSheet(
                f"color: {DARK['fg2']}; font-size: 9.5pt; background: transparent; border: none;"
            )
            info["icon_widget"].setIcon(info["icon_fif"].icon(color=QColor(DARK["fg2"])))

    def _select_theme(self, selected_key: str):
        if selected_key == self._current_theme:
            return
        for btn, info in self._theme_buttons.items():
            btn.setChecked(info["key"] == selected_key)
            self._style_theme_button(btn)
        self._current_theme = selected_key
        self.chosen_theme = selected_key
        self._rebuild_swatches(selected_key, keep_selection=True)

    def _rebuild_swatches(self, theme_key: str, keep_selection: bool = True):
        selected = self._current_accent
        if keep_selection:
            for btn, key in self._accent_buttons.items():
                if btn.isChecked():
                    selected = key
                    break

        while self._swatch_layout.count():
            item = self._swatch_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            elif item.layout() is not None:
                self._clear_layout(item.layout())

        self._accent_buttons = {}
        self._accent_group = QButtonGroup(self)

        preset_source = ACCENT_PRESETS_LIGHT if theme_key == "light" else ACCENT_PRESETS_DARK
        if selected not in preset_source:
            selected = next(iter(preset_source))
        self._current_accent = selected

        keys = list(preset_source.items())
        for i, (key, preset) in enumerate(keys):
            accent_hex = preset["accent"]
            r, g, b = hex_to_rgb(accent_hex)

            dot = QRadioButton()
            dot.setCursor(Qt.PointingHandCursor)
            dot.setStyleSheet(
                f"QRadioButton {{ background: transparent; }}"
                f"QRadioButton::indicator {{ width: 14px; height: 14px; border: 1px solid {DARK['border']}; "
                f"border-radius: 7px; background: {DARK['indicator_bg']}; }}"
                f"QRadioButton::indicator:hover {{ border: 1px solid {DARK['accent']}; }}"
                f"QRadioButton::indicator:checked {{ background: transparent; border: 4px solid {DARK['accent']}; }}"
            )
            dot.setChecked(key == selected)

            row = _AccentRow(dot, (r, g, b))
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 8, 12, 8)
            row_layout.setSpacing(12)

            swatch = QLabel()
            swatch.setFixedSize(18, 18)
            swatch.setStyleSheet(
                f"background-color: {accent_hex}; border-radius: 5px; "
                f"border: 1px solid {DARK['border_soft2']};"
            )
            swatch.setAttribute(Qt.WA_TransparentForMouseEvents)
            row_layout.addWidget(swatch)

            lbl = QLabel(T(self._LABEL_KEYS.get(key, key)))
            lbl.setStyleSheet(f"color: {DARK['fg']}; font-size: 9.5pt; background: transparent; border: none;")
            lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
            row_layout.addWidget(lbl)

            row_layout.addStretch()
            row_layout.addWidget(dot)

            dot.toggled.connect(lambda _checked, rw=row: rw._restyle())
            self._accent_group.addButton(dot)
            self._accent_buttons[dot] = key
            self._swatch_layout.addWidget(row)

            if i < len(keys) - 1:
                self._swatch_layout.addWidget(h_separator())

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _apply(self):
        self.chosen_theme = self._current_theme
        for btn, key in self._accent_buttons.items():
            if btn.isChecked():
                self.chosen_accent = key
                break
        self.accept()
