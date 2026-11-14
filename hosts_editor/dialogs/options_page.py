import os
import webbrowser

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QWidget, QFrame, QScrollArea, QPushButton, QSlider,
    QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, QRectF, QSize, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen

from ..icons import FIF
from ..ui_parts import IconWidget
from ..constants import (
    DARK, ACCENT_PRESETS_DARK, ACCENT_PRESETS_LIGHT, ACRYLIC_SUPPORTED, DEFAULT_EFFECTS, DEFAULT_MATERIAL,
    DEFAULT_TRANSPARENCY, EFFECTS, MATERIAL, accent_rgba, clamp_transparency, saved_glow, valid_accent, valid_material, valid_theme,
    load_settings, save_settings, updates_on_startup,
)
from ..widgets_qt import (
    HOTSPage, HOTSDialog, HOTSButton, HOTSSwitch, colored_svg_icon, attach_fluent_tip, SmoothWheel,
)
from ..i18n import T, LANGUAGES, current_lang
from ..bg_tasks import register_qthread, is_shutting_down
from ..password_utils import hash_password, verify_password

from ._about_shared import APP_VERSION, _UpdateCheckWorker, _DownloadWorker, _parse_version
from .password_dialog import _pass_field

_ACCENT_LABEL_KEYS = {
    "gold": "acc_gold",
    "red": "acc_red",
    "green": "acc_green",
    "blue": "acc_blue",
    "teal": "acc_teal",
    "graphite": "acc_graphite",
}


def _title_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent; border: none;")
    return lbl


def _desc_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
    return lbl


def _row_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setMinimumWidth(110)
    lbl.setStyleSheet(f"color: {DARK['fg']}; font-size: 9.5pt; background: transparent; border: none;")
    return lbl


def _field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {DARK['fg']}; font-size: 9pt; background: transparent; border: none;")
    return lbl


def _rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


class _Choice(QPushButton):
    def __init__(self, text: str, icon=None, min_width: int = 0):
        super().__init__(text)
        self._icon = icon
        self._selected = False
        self.setFixedHeight(34)
        if min_width:
            self.setMinimumWidth(min_width)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setIconSize(QSize(15, 15))
        self._apply()

    def set_selected(self, selected: bool):
        if selected != self._selected:
            self._selected = selected
            self._apply()

    def _apply(self):
        if self._selected:
            qss = (
                f"QPushButton {{ background-color: {accent_rgba(0.28)}; border: 1px solid {accent_rgba(0.55)}; "
                f"border-radius: 6px; color: #ffffff; font-size: 9pt; font-weight: 600; padding: 0px 14px; }}"
                f"QPushButton:hover {{ background-color: {accent_rgba(0.42)}; border-color: {accent_rgba(0.85)}; }}"
            )
            icon_color = QColor("#ffffff")
        else:
            r, g, b = _rgb(DARK["fg2"])
            qss = (
                f"QPushButton {{ background-color: rgba({r},{g},{b},18); border: 1px solid rgba({r},{g},{b},55); "
                f"border-radius: 6px; color: {DARK['fg']}; font-size: 9pt; padding: 0px 14px; }}"
                f"QPushButton:hover {{ background-color: rgba({r},{g},{b},50); border-color: rgba({r},{g},{b},115); }}"
            )
            icon_color = QColor(DARK["fg2"])
        self.setStyleSheet(qss)
        if self._icon is not None:
            self.setIcon(colored_svg_icon(self._icon, icon_color, sizes=(15,)))


class _Swatch(QPushButton):
    def __init__(self):
        super().__init__()
        self._color = QColor("#888888")
        self._selected = False
        self._hover = False
        self.setFixedSize(34, 34)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)

    def set_state(self, color_hex: str, selected: bool):
        self._color = QColor(color_hex)
        self._selected = selected
        self.update()

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        bg = QColor(self._color)
        bg.setAlpha(54 if self._hover else (46 if self._selected else 18))
        border = QColor(self._color)
        border.setAlpha(230 if self._selected else (130 if self._hover else 55))
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        p.setPen(QPen(border, 1.5 if self._selected else 1.0))
        p.setBrush(bg)
        p.drawRoundedRect(rect, 6, 6)
        p.setPen(Qt.NoPen)
        p.setBrush(self._color)
        radius = 7.0 if self._selected else 5.5
        p.drawEllipse(rect.center(), radius, radius)
        p.end()


def _transparent_panel() -> QWidget:
    panel = QWidget()
    panel.setStyleSheet("background: transparent; border: none;")
    return panel


class _Header(QWidget):
    clicked = Signal()

    def __init__(self, clickable: bool):
        super().__init__()
        self._clickable = clickable
        self.setStyleSheet("background: transparent; border: none;")
        if clickable:
            self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if self._clickable and event.button() == Qt.LeftButton:
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if (self._clickable and event.button() == Qt.LeftButton
                and self.rect().contains(event.position().toPoint())):
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class _Card(QFrame):
    expanded = Signal(object)

    HEADER_HEIGHT = 72

    def __init__(self, icon, title: str, sub: QWidget, clickable: bool):
        super().__init__()
        self.setObjectName("optCard")
        self.setStyleSheet(
            f"QFrame#optCard {{ background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; "
            f"border-radius: 6px; }}"
        )
        self._expanded = False
        self._panel = None
        self._sep = None
        self._chevron = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self._outer = outer

        self.header = _Header(clickable)
        self.header.setFixedHeight(self.HEADER_HEIGHT)
        h = QHBoxLayout(self.header)
        h.setContentsMargins(16, 0, 16, 0)
        h.setSpacing(10)
        self._header_lay = h

        ico = IconWidget(icon)
        ico.setFixedSize(20, 20)
        ico.setIcon(colored_svg_icon(icon, QColor(DARK["accent"]), sizes=(20,)))
        h.addWidget(ico, 0, Qt.AlignVCenter)

        col = QVBoxLayout()
        col.setSpacing(2)
        col.addStretch()
        self._title_lbl = _title_label(title)
        col.addWidget(self._title_lbl)
        col.addWidget(sub)
        col.addStretch()
        h.addLayout(col, 1)

        outer.addWidget(self.header)

    def set_title(self, text: str):
        self._title_lbl.setText(text)

    def add_side(self, widget: QWidget):
        self._header_lay.addWidget(widget, 0, Qt.AlignVCenter)

    def _add_chevron(self):
        btn = HOTSButton(FIF.CHEVRON_RIGHT_MED, DARK["fg2"], "", accent=False, glyph_color=DARK["accent"])
        btn.setFixedWidth(44)
        self.add_side(btn)
        self._chevron = btn
        return btn

    def make_navigable(self, callback):
        btn = self._add_chevron()
        btn.clicked.connect(callback)
        self.header.clicked.connect(callback)

    def make_expandable(self, panel: QWidget):
        btn = self._add_chevron()
        btn.clicked.connect(self.toggle)
        self.header.clicked.connect(self.toggle)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {DARK['border_faint']}; border: none;")
        sep.setVisible(False)
        self._outer.addWidget(sep)
        self._sep = sep

        panel.setVisible(False)
        self._outer.addWidget(panel)
        self._panel = panel

    def is_expanded(self) -> bool:
        return self._expanded

    def toggle(self):
        self.set_expanded(not self._expanded)

    def set_expanded(self, expanded: bool):
        if expanded == self._expanded:
            return
        self._expanded = expanded
        self._panel.setVisible(expanded)
        self._sep.setVisible(expanded)
        self._chevron.set_icon(
            FIF.CHEVRON_DOWN_MED if expanded else FIF.CHEVRON_RIGHT_MED,
            color=DARK["fg2"], glyph_color=DARK["accent"],
        )
        if expanded:
            self.expanded.emit(self)


class OptionsPage(HOTSPage):
    def __init__(self, parent=None, on_about=None, on_support=None, on_language=None, on_appearance=None,
                 on_live_glow=None, on_live_transparency=None, on_table_text_accent=None, on_restart=None, get_password_hash=None, set_password_hash=None):
        super().__init__("optionsInterface", FIF.SETTING, T("btn_options"), parent)
        self._update_worker = None
        self._download_worker = None
        self._known_update_url = None
        self._known_update_asset = None
        self._on_language = on_language
        self._on_appearance = on_appearance
        self._on_live_glow = on_live_glow
        self._on_live_transparency = on_live_transparency
        self._on_table_text_accent = on_table_text_accent
        self._on_restart = on_restart
        self._get_password_hash = get_password_hash
        self._set_password_hash = set_password_hash
        self._pw_hash = ""
        self._build(on_about, on_support)

    def refresh_content(self):
        self._refresh_password_state()

    def _build(self, on_about, on_support):
        cl = self.content_layout

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        SmoothWheel(scroll)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(12)

        about = _Card(FIF.INFO, T("opt_about"), _desc_label(T("opt_about_desc")), clickable=True)
        about.make_navigable(on_about)
        lay.addWidget(about)

        support = _Card(FIF.HEART, T("opt_support"), _desc_label(T("opt_support_desc")), clickable=True)
        support.make_navigable(on_support)
        lay.addWidget(support)

        self._pw_card = _Card(FIF.FINGERPRINT, T("opt_pass_off"), _desc_label(T("opt_password_desc")), clickable=True)
        self._pw_card.make_expandable(self._build_password_panel())
        lay.addWidget(self._pw_card)

        language = _Card(FIF.LANGUAGE, T("opt_language"), _desc_label(T("opt_language_desc")), clickable=True)
        language.make_expandable(self._build_language_panel())
        lay.addWidget(language)

        appearance = _Card(FIF.PALETTE, T("opt_appearance"), _desc_label(T("opt_appearance_desc")), clickable=True)
        appearance.make_expandable(self._build_appearance_panel())
        lay.addWidget(appearance)

        expandable = (self._pw_card, language, appearance)
        for card in expandable:
            card.expanded.connect(
                lambda opened, cards=expandable: [c.set_expanded(False) for c in cards if c is not opened])

        lay.addWidget(self._build_updates_card())
        lay.addStretch()

        scroll.setWidget(inner)
        cl.addWidget(scroll, 1)

        self._refresh_password_state()

    def _build_password_panel(self) -> QWidget:
        panel = _transparent_panel()
        v = QVBoxLayout(panel)
        v.setContentsMargins(16, 12, 16, 14)
        v.setSpacing(8)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(4)
        self._pw_grid = grid

        self._pw_old = _pass_field()
        self._pw_new = _pass_field()
        self._pw_rep = _pass_field()
        self._pw_old_lbl = _field_label(T("pwd_lbl_current"))
        fields = (
            (self._pw_old_lbl, self._pw_old),
            (_field_label(T("pwd_lbl_new")), self._pw_new),
            (_field_label(T("pwd_lbl_repeat")), self._pw_rep),
        )
        for col, (lbl, edit) in enumerate(fields):
            grid.addWidget(lbl, 0, col)
            grid.addWidget(edit, 1, col)
            grid.setColumnStretch(col, 1)
        v.addLayout(grid)

        row = QHBoxLayout()
        row.setSpacing(8)
        self._pw_err = QLabel("")
        self._pw_err.setWordWrap(True)
        self._pw_err.setStyleSheet("color: #ff6060; font-size: 8pt; background: transparent; border: none;")
        row.addWidget(self._pw_err, 1)

        self._pw_save = HOTSButton(FIF.SAVE, "#ffffff", T("pwd_btn_set"), accent=True)
        self._pw_save.fit_to_content(min_width=100)
        self._pw_save.clicked.connect(self._save_password)
        row.addWidget(self._pw_save)

        self._pw_remove = HOTSButton(FIF.DELETE, DARK["red"], T("pwd_btn_remove"))
        self._pw_remove.fit_to_content(min_width=100)
        self._pw_remove.clicked.connect(self._remove_password)
        row.addWidget(self._pw_remove)
        v.addLayout(row)

        self._pw_rep.returnPressed.connect(self._save_password)
        return panel

    def _refresh_password_state(self):
        if not hasattr(self, "_pw_card"):
            return
        self._pw_hash = self._get_password_hash() if self._get_password_hash is not None else ""
        has = bool(self._pw_hash)
        self._pw_card.set_title(T("opt_pass_on") if has else T("opt_pass_off"))
        self._pw_old_lbl.setVisible(has)
        self._pw_old.setVisible(has)
        self._pw_remove.setVisible(has)
        self._pw_grid.setColumnStretch(0, 1 if has else 0)
        for edit in (self._pw_old, self._pw_new, self._pw_rep):
            edit.clear()
        self._pw_err.setText("")

    def _password_error(self, key: str, focus=None, clear=None):
        self._pw_err.setText(T(key))
        if clear is not None:
            clear.clear()
        if focus is not None:
            focus.setFocus()

    def _check_current_password(self, missing_key: str) -> bool:
        if not self._pw_hash:
            return True
        current = self._pw_old.text()
        if not current:
            self._password_error(missing_key, focus=self._pw_old)
            return False
        if not verify_password(current, self._pw_hash):
            self._password_error("pwd_err_wrong", focus=self._pw_old, clear=self._pw_old)
            return False
        return True

    def _save_password(self):
        if not self._check_current_password("pwd_err_no_current"):
            return
        new_val = self._pw_new.text()
        if not new_val:
            self._password_error("pwd_err_empty", focus=self._pw_new)
            return
        if len(new_val) < 4:
            self._password_error("pwd_err_too_short", focus=self._pw_new)
            return
        if new_val != self._pw_rep.text():
            self._password_error("pwd_err_mismatch", focus=self._pw_rep, clear=self._pw_rep)
            return
        if self._set_password_hash is None or not self._set_password_hash(hash_password(new_val)):
            self._password_error("pwd_err_save_failed")
            return
        self._refresh_password_state()
        HOTSDialog.info(self, T("pwd_set_ok_title"), T("pwd_set_ok_msg"))

    def _remove_password(self):
        if not self._check_current_password("pwd_err_no_for_remove"):
            return
        if self._set_password_hash is None or not self._set_password_hash(""):
            self._password_error("pwd_err_save_failed")
            return
        self._refresh_password_state()
        HOTSDialog.info(self, T("pwd_remove_ok_title"), T("pwd_remove_ok_msg"))

    def _build_language_panel(self) -> QWidget:
        panel = _transparent_panel()
        row = QHBoxLayout(panel)
        row.setContentsMargins(16, 12, 16, 14)
        row.setSpacing(6)

        self._lang_btns = {}
        for code, name in LANGUAGES.items():
            btn = _Choice(code.upper(), min_width=56)
            attach_fluent_tip(btn, name)
            btn.clicked.connect(lambda _c=False, c=code: self._select_language(c))
            row.addWidget(btn)
            self._lang_btns[code] = btn
        row.addStretch()
        self._restyle_languages()
        return panel

    def _restyle_languages(self):
        active = current_lang()
        for code, btn in self._lang_btns.items():
            btn.set_selected(code == active)

    def _select_language(self, code: str):
        if code != current_lang() and self._on_language is not None:
            self._on_language(code)
        self._restyle_languages()

    def _build_appearance_panel(self) -> QWidget:
        s = load_settings()
        self._ap = {
            "accent_color": valid_accent(s.get("accent_color")),
            "theme": valid_theme(s.get("theme")),
            "glow": saved_glow(s),
            "transparency": clamp_transparency(s.get("transparency", DEFAULT_TRANSPARENCY)),
            "material": valid_material(s.get("material", DEFAULT_MATERIAL)),
            "effects": s.get("effects", DEFAULT_EFFECTS) is not False,
        }
        self._ap_initial = dict(self._ap)

        panel = _transparent_panel()
        v = QVBoxLayout(panel)
        v.setContentsMargins(16, 12, 16, 14)
        v.setSpacing(10)

        theme_row = QHBoxLayout()
        theme_row.setSpacing(6)
        theme_lbl = _row_label(T("app_theme_label"))
        theme_row.addWidget(theme_lbl)
        self._theme_btns = {}
        for key, label_key, icon in (
            ("dark", "app_theme_dark", FIF.QUIET_HOURS),
            ("light", "app_theme_light", FIF.BRIGHTNESS),
        ):
            btn = _Choice(T(label_key), icon, min_width=96)
            btn.clicked.connect(lambda _c=False, k=key: self._set_theme(k))
            theme_row.addWidget(btn)
            self._theme_btns[key] = btn
        theme_row.addStretch()

        self._swatch_btns = {}
        for key in ACCENT_PRESETS_DARK:
            btn = _Swatch()
            attach_fluent_tip(btn, T(_ACCENT_LABEL_KEYS.get(key, key)))
            btn.clicked.connect(lambda _c=False, k=key: self._set_accent(k))
            theme_row.addWidget(btn)
            self._swatch_btns[key] = btn
        v.addLayout(theme_row)

        self._table_text_cb = HOTSSwitch(T("acc_table_text_accent"), font_pt=9, spacing=10)
        self._table_text_cb.setChecked(bool(s.get("table_text_accent", False)))
        self._table_text_cb.toggled.connect(self._on_table_text_toggled)
        v.addWidget(self._table_text_cb)

        dependents = []

        material_row = QHBoxLayout()
        material_row.setSpacing(6)
        self._material_btns = {}
        if ACRYLIC_SUPPORTED:
            mat_lbl = _row_label(T("app_material_label"))
            material_row.addWidget(mat_lbl)
            dependents.append((mat_lbl, "effects"))
            for key, label_key in (("mica", "app_material_mica"), ("acrylic", "app_material_acrylic")):
                btn = _Choice(T(label_key), min_width=96)
                btn.clicked.connect(lambda _c=False, k=key: self._set_material(k))
                material_row.addWidget(btn)
                dependents.append((btn, "effects"))
                self._material_btns[key] = btn
        material_row.addStretch()

        self._effects_cb = HOTSSwitch(T("app_effects_label"), font_pt=9, spacing=10)
        self._effects_cb.setChecked(self._ap["effects"])
        self._effects_cb.toggled.connect(self._set_effects)
        material_row.addWidget(self._effects_cb)
        v.addLayout(material_row)

        self._glow_lbl, self._glow_slider, self._glow_value = self._add_slider_row(
            v, T("app_glow_label"), self._ap["glow"], self._on_glow_changed)
        dependents += [(self._glow_lbl, "live"), (self._glow_slider, "live"), (self._glow_value, "live")]

        if ACRYLIC_SUPPORTED:
            self._trans_lbl, self._trans_slider, self._trans_value = self._add_slider_row(
                v, T("app_transparency_label"), self._ap["transparency"], self._on_transparency_changed)
            dependents += [(self._trans_lbl, "acrylic"), (self._trans_slider, "acrylic"), (self._trans_value, "acrylic")]

        self._ap_timer = QTimer(self)
        self._ap_timer.setSingleShot(True)
        self._ap_timer.setInterval(350)
        self._ap_timer.timeout.connect(self._commit_appearance)

        self._restart_row = _transparent_panel()
        restart_lay = QHBoxLayout(self._restart_row)
        restart_lay.setContentsMargins(0, 4, 0, 0)
        restart_lay.setSpacing(12)
        restart_lbl = _desc_label(T("app_restart_msg"))
        restart_lay.addWidget(restart_lbl, 1)
        restart_btn = HOTSButton(FIF.SYNC, "#ffffff", T("btn_restart_now"), accent=True)
        restart_btn.fit_to_content()
        restart_btn.clicked.connect(self._restart)
        restart_lay.addWidget(restart_btn)
        self._restart_row.setVisible(False)
        restart_policy = self._restart_row.sizePolicy()
        restart_policy.setRetainSizeWhenHidden(True)
        self._restart_row.setSizePolicy(restart_policy)
        v.addWidget(self._restart_row)

        self._effects_dependents = dependents
        self._effects_opacity = []
        for w, _kind in dependents:
            eff = QGraphicsOpacityEffect(w)
            w.setGraphicsEffect(eff)
            self._effects_opacity.append(eff)

        self._restyle_appearance()
        return panel

    def _restyle_appearance(self):
        ap = self._ap
        for key, btn in self._theme_btns.items():
            btn.set_selected(key == ap["theme"])

        presets = ACCENT_PRESETS_LIGHT if ap["theme"] == "light" else ACCENT_PRESETS_DARK
        for key, btn in self._swatch_btns.items():
            btn.set_state(presets[key]["accent"], key == ap["accent_color"])

        for key, btn in self._material_btns.items():
            btn.set_selected(key == ap["material"])

        self._glow_value.setText(f"{ap['glow']}%")
        if ACRYLIC_SUPPORTED:
            self._trans_value.setText(f"{ap['transparency']}%")

        live = ap["effects"] and EFFECTS
        states = {
            "effects": ap["effects"],
            "live": live,
            "acrylic": live and ap["material"] == "acrylic" and MATERIAL == "acrylic",
        }
        for (w, kind), eff in zip(self._effects_dependents, self._effects_opacity):
            active = states[kind]
            w.setEnabled(active)
            eff.setOpacity(1.0 if active else 0.4)
            attach_fluent_tip(w, "" if active else T(self._inactive_tip_key(kind, ap)), width=260, delay_ms=400)

    @staticmethod
    def _inactive_tip_key(kind: str, ap: dict) -> str:
        if not ap["effects"]:
            return "app_tip_need_effects"
        if kind == "acrylic" and ap["material"] != "acrylic":
            return "app_tip_acrylic_only"
        return "app_tip_restart"

    def _set_theme(self, key: str):
        self._change_appearance(theme=key)

    def _set_accent(self, key: str):
        self._change_appearance(accent_color=key)

    def _set_material(self, key: str):
        self._change_appearance(material=key)

    def _set_effects(self, enabled: bool):
        self._change_appearance(effects=bool(enabled))

    def _change_appearance(self, **changes):
        if all(self._ap[k] == v for k, v in changes.items()):
            return
        self._ap.update(changes)
        self._restyle_appearance()
        self._commit_appearance()

    def _on_table_text_toggled(self, checked: bool):
        if self._on_table_text_accent is not None:
            self._on_table_text_accent(bool(checked))

    def _add_slider_row(self, layout, label_text: str, value: int, on_changed):
        row = QHBoxLayout()
        row.setSpacing(12)
        lbl = _row_label(label_text)
        value_lbl = QLabel()
        value_lbl.setMinimumWidth(40)
        value_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        value_lbl.setStyleSheet(
            f"color: {DARK['fg2']}; font-size: 9.5pt; background: transparent; border: none;")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(value)
        slider.setCursor(Qt.PointingHandCursor)
        slider.setFixedHeight(24)
        slider.setStyleSheet(
            f"QSlider::groove:horizontal {{ height: 4px; background: {DARK['border']}; border-radius: 2px; }}"
            f"QSlider::sub-page:horizontal {{ background: {DARK['accent']}; border-radius: 2px; }}"
            f"QSlider::handle:horizontal {{ background: {DARK['accent']}; width: 14px; height: 14px; "
            f"margin: -5px 0; border-radius: 7px; }}"
        )
        slider.valueChanged.connect(on_changed)
        slider.sliderReleased.connect(self._flush_appearance)
        row.addWidget(lbl)
        row.addWidget(slider, 1)
        row.addWidget(value_lbl)
        layout.addLayout(row)
        return lbl, slider, value_lbl

    def _on_glow_changed(self, value: int):
        self._ap["glow"] = value
        self._glow_value.setText(f"{value}%")
        if self._on_live_glow is not None:
            self._on_live_glow(value)
        self._ap_timer.start()

    def _on_transparency_changed(self, value: int):
        self._ap["transparency"] = value
        self._trans_value.setText(f"{value}%")
        if self._on_live_transparency is not None:
            self._on_live_transparency(value)
        self._ap_timer.start()

    def _flush_appearance(self):
        self._ap_timer.stop()
        self._commit_appearance()

    def _commit_appearance(self):
        if self._on_appearance is not None:
            self._on_appearance(dict(self._ap))
        self._restart_row.setVisible(self._restart_needed())

    def _restart_needed(self) -> bool:
        keys = [k for k in self._ap if k != "glow"]
        if not (ACRYLIC_SUPPORTED and "acrylic" in (self._ap["material"], self._ap_initial["material"])):
            keys.remove("transparency")
        return any(self._ap[k] != self._ap_initial[k] for k in keys)

    def _restart(self):
        self._ap_timer.stop()
        self._commit_appearance()
        if self._on_restart is not None:
            self._on_restart()

    def _build_updates_card(self) -> QWidget:
        self._update_startup_cb = HOTSSwitch(T("about_check_update_startup"), font_pt=8.5, color=DARK["fg2"], spacing=8)
        self._update_startup_cb.setChecked(updates_on_startup(load_settings()))
        self._update_startup_cb.toggled.connect(self._on_check_update_startup_toggled)

        card = _Card(FIF.SYNC, T("opt_updates"), self._update_startup_cb, clickable=False)

        self._update_btn = HOTSButton(FIF.SYNC, "#60c8ff", T("about_check_update"))
        self._update_btn.fit_to_content()
        self._update_btn.clicked.connect(self._check_for_updates)
        card.add_side(self._update_btn)
        return card

    def _on_check_update_startup_toggled(self, checked: bool):
        fresh = load_settings()
        fresh["check_updates_on_startup"] = bool(checked)
        save_settings(fresh)

    def _refresh_update_button(self):
        if self._known_update_url:
            self._update_btn.set_icon(FIF.DOWNLOAD, "#60c8ff")
            self._update_btn.set_label(T("about_download_update"))
        else:
            self._update_btn.set_icon(FIF.SYNC, "#60c8ff")
            self._update_btn.set_label(T("about_check_update"))
        self._update_btn.fit_to_content()

    def _check_for_updates(self):
        if self._download_worker is not None:
            return
        if self._known_update_url:
            self._open_known_update()
            return
        if self._update_worker is not None and self._update_worker.isRunning():
            return

        self._update_btn.setEnabled(False)
        self._update_btn.set_label(T("about_checking_update"))
        self._update_btn.fit_to_content()

        self._update_worker = _UpdateCheckWorker(self)
        self._update_worker.finished_ok.connect(self._on_update_check_ok)
        self._update_worker.failed.connect(self._on_update_check_failed)
        self._update_worker.finished.connect(self._reset_update_button)
        self._update_worker.finished.connect(self._update_worker.deleteLater)
        register_qthread(self._update_worker)
        self._update_worker.start()

    def _reset_update_button(self):
        if is_shutting_down():
            return
        self._update_worker = None
        self._update_btn.setEnabled(True)
        self._refresh_update_button()

    def apply_known_update(self, tag: str, url: str, asset=None):
        self._known_update_url = url
        self._known_update_asset = asset
        self._refresh_update_button()

    def _open_known_update(self):
        if self._known_update_asset:
            self._start_download(self._known_update_asset)
            return
        webbrowser.open(self._known_update_url)
        self._known_update_url = None
        self._refresh_update_button()

    def _start_download(self, asset: dict):
        self._update_btn.setEnabled(False)
        self._update_btn.set_label(T("about_dl_progress", pct=0))
        self._update_btn.fit_to_content()

        worker = _DownloadWorker(asset, self)
        self._download_worker = worker
        worker.progress.connect(self._on_download_progress)
        worker.finished_ok.connect(self._on_download_ok)
        worker.failed.connect(self._on_download_failed)
        worker.finished.connect(self._reset_after_download)
        worker.finished.connect(worker.deleteLater)
        register_qthread(worker)
        worker.start()

    def _on_download_progress(self, pct: int):
        self._update_btn.set_label(T("about_dl_progress", pct=pct))
        self._update_btn.fit_to_content()

    def _reset_after_download(self):
        if is_shutting_down():
            return
        self._download_worker = None
        self._update_btn.setEnabled(True)
        self._refresh_update_button()

    def _on_download_ok(self, path: str):
        self._known_update_url = None
        self._known_update_asset = None
        if HOTSDialog.ask(self, T("about_dl_done_title"), T("about_dl_done_msg", path=path)):
            try:
                os.startfile(os.path.dirname(path))
            except OSError:
                pass

    def _on_download_failed(self, error: str):
        HOTSDialog.error(self, T("about_dl_error_title"), error)

    def _on_update_check_ok(self, latest_tag: str, release_url: str, asset):
        if _parse_version(latest_tag) > _parse_version(APP_VERSION):
            self.apply_known_update(latest_tag, release_url, asset)
            msg_key = "about_update_available_dl_msg" if asset else "about_update_available_msg"
            open_it = HOTSDialog.ask(
                self,
                T("about_update_available_title"),
                T(msg_key).format(version=latest_tag, current=APP_VERSION),
            )
            if open_it:
                self._open_known_update()
        else:
            HOTSDialog.info(
                self,
                T("about_update_uptodate_title"),
                T("about_update_uptodate_msg").format(current=APP_VERSION),
            )

    def _on_update_check_failed(self, error: str):
        HOTSDialog.error(
            self,
            T("about_update_error_title"),
            T("about_update_error_msg").format(error=error),
        )
