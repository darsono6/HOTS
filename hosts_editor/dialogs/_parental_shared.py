import os
import sys
import threading

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal, QObject

from qfluentwidgets import FluentIcon as FIF

from ..constants import DARK, load_settings, save_settings, accent_rgba
from ..core import toggle_parental_control, HostsLimitExceeded, MAX_ACTIVE_ENTRIES
from ..widgets_qt import HOTSButton, HOTSDialog
from ..i18n import T


def _blocklists_dir() -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "blocklists")
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "..", "blocklists")


CATEGORIES = [
    {"label_key": "par_cat_adult",     "icon": "🔞", "color": "#cc2222", "file": "adult.txt"},
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
    {"label_key": "par_cat_torrent",   "icon": "⛔", "color": "#aaaaaa", "file": "torrent.txt"},
]

_CF_ACCENT = DARK["accent"]


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _comment_for_category(cat: dict) -> str:
    suffix = cat["file"][:-4] if cat["file"].endswith(".txt") else cat["file"]
    name_key = f"par_comment_name_{suffix}"
    name = T(name_key)
    if name == name_key:
        name = T(cat["label_key"])
    return f"{T('par_comment_prefix')}: {name}"


_CATEGORY_COMMENT = {cat["file"]: _comment_for_category(cat) for cat in CATEGORIES}
_CATEGORY_COMMENT["telemetry.txt"] = _comment_for_category(
    {"file": "telemetry.txt", "label_key": "par_cat_antispy_domains"}
)


class _ToggleSignals(QObject):
    done = Signal(bool, object)


class _ParentalCardMixin:

    def _make_card(self, cat: dict, active: bool = None) -> QWidget:
        list_path = os.path.join(self._bdir, cat["file"])
        file_ok = os.path.exists(list_path)
        card = self._card_frame(cat["color"])
        info_lay = card.property("info_lay")

        title_row = QHBoxLayout()
        ico = QLabel(cat["icon"])
        ico.setStyleSheet(f"color: {_hex_to_rgba(cat['color'], 0.85)}; font-size: 18px; background: transparent;")
        title_row.addWidget(ico)
        t = QLabel(T(cat["label_key"]))
        t.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent;")
        title_row.addWidget(t)
        title_row.addStretch()
        info_lay.addLayout(title_row)

        file_txt = T("par_file_ok", file=cat["file"]) if file_ok else T("par_file_missing", file=cat["file"])
        file_fg  = DARK["fg2"] if file_ok else DARK["red"]
        fl = QLabel(file_txt)
        fl.setStyleSheet(f"color: {file_fg}; font-size: 9pt; background: transparent;")
        info_lay.addWidget(fl)

        if active is None:
            from ..core import is_parental_active
            active = is_parental_active(tag_suffix=cat["file"])
        is_disabled = not active and not file_ok
        btn_color = DARK["red"] if active else (DARK["green"] if not is_disabled else DARK["bg3"])
        btn_label = (T("par_btn_disable") if active
                     else (T("par_btn_enable") if not is_disabled else T("par_btn_no_file")))
        btn_icon  = FIF.CLOSE if active else FIF.ACCEPT

        btn = HOTSButton(btn_icon, btn_color, btn_label, accent=False)
        btn.fit_to_content()
        btn.setEnabled(not is_disabled)

        state = {
            "active": active,
            "cat":    cat,
            "path":   list_path,
            "btn":    btn,
        }
        self._states[cat["file"]] = state
        btn.clicked.connect(lambda _checked=False, s=state: self._toggle(s))

        btn_row = card.property("btn_lay")
        btn_row.addWidget(btn)

        return card

    def _card_frame(self, accent_color: str) -> QWidget:
        outer = QWidget()
        outer.setStyleSheet(f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;")
        outer.setFixedHeight(64)
        outer_lay = QHBoxLayout(outer)
        outer_lay.setContentsMargins(0, 0, 0, 0)
        outer_lay.setSpacing(0)

        info = QWidget()
        info.setStyleSheet("background: transparent; border: none;")
        info_lay = QVBoxLayout(info)
        info_lay.setContentsMargins(16, 10, 0, 10)
        info_lay.setSpacing(3)
        outer_lay.addWidget(info, 1)

        btn_area = QWidget()
        btn_area.setStyleSheet("background: transparent; border: none;")
        btn_lay = QHBoxLayout(btn_area)
        btn_lay.setContentsMargins(8, 0, 12, 0)
        btn_lay.setSpacing(8)
        btn_lay.setAlignment(Qt.AlignCenter)
        outer_lay.addWidget(btn_area)

        outer.setProperty("info_lay", info_lay)
        outer.setProperty("btn_lay",  btn_lay)
        return outer

    def _toggle(self, state: dict):
        cat    = state["cat"]
        target = not state["active"]
        path   = state["path"]

        if target and not os.path.exists(path):
            HOTSDialog.error(self, T("par_err_no_file_title"),
                             T("par_err_no_file_msg", path=path, file=cat["file"]))
            return

        if not self._confirm_overwrite_unsaved():
            return

        self._apply_toggle(state, target)

    def _confirm_overwrite_unsaved(self) -> bool:
        if self._parent_win and getattr(self._parent_win, "_dirty", False):
            return HOTSDialog.ask(self, T("par_dirty_warn_title"), T("par_dirty_warn_msg"))
        return True

    def _apply_toggle(self, state: dict, target: bool):
        cat  = state["cat"]
        path = state["path"]
        btn  = state["btn"]
        comment = _comment_for_category(cat)

        if not os.path.exists(path):
            self._on_apply_toggle_done(state, target, True, None)
            return

        btn.setEnabled(False)

        signals = _ToggleSignals()
        if not hasattr(self, "_toggle_signal_refs"):
            self._toggle_signal_refs = []
        self._toggle_signal_refs.append(signals)

        def _cleanup_and_handle(ok, limit_exc):
            if signals in self._toggle_signal_refs:
                self._toggle_signal_refs.remove(signals)
            self._on_apply_toggle_done(state, target, ok, limit_exc)

        signals.done.connect(_cleanup_and_handle)

        def worker():
            ok = True
            limit_exc = None
            try:
                ok = toggle_parental_control(target, path, tag_suffix=cat["file"],
                                             comment=comment)
            except HostsLimitExceeded as exc:
                limit_exc = exc
                ok = False
            signals.done.emit(ok, limit_exc)

        threading.Thread(target=worker, daemon=True).start()

    def _on_apply_toggle_done(self, state: dict, target: bool, ok: bool, limit_exc):
        cat = state["cat"]
        btn = state["btn"]
        btn.setEnabled(True)

        if limit_exc is not None:
            HOTSDialog.error(self, T("save_limit_title"),
                             T("save_limit_msg", n=limit_exc.would_be_count, max=MAX_ACTIVE_ENTRIES))
            return

        if ok:
            state["active"] = target
            self._refresh_btn(state)
            if self._parent_win and hasattr(self._parent_win, "_load"):
                self._parent_win._load()
            msg_key = "par_success_on" if target else "par_success_off"
            HOTSDialog.info(self, T("par_success_title"),
                            T(msg_key, label=T(cat["label_key"])))
        else:
            self._refresh_btn(state)
            HOTSDialog.error(self, T("par_err_hosts_title"), T("par_err_hosts_msg"))

    def _refresh_btn(self, state: dict):
        btn    = state["btn"]
        active = state["active"]
        color  = DARK["red"] if active else DARK["green"]
        label  = T("par_btn_disable") if active else T("par_btn_enable")
        icon   = FIF.CLOSE if active else FIF.ACCEPT

        btn.set_label(label)
        btn.set_icon(icon, color)
        btn.set_accent(False)
        btn.fit_to_content()


class _InfoButton(QWidget):

    _SIZE = 16
    _POPUP_W = 260
    _COLOR_ON  = DARK["accent"]
    _COLOR_OFF = DARK["border"]

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self._text = text
        self._popup: "QWidget | None" = None
        self._hovered = False
        self.setFixedSize(self._SIZE, self._SIZE)
        self.setCursor(Qt.PointingHandCursor)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self._lbl = QLabel("?")
        self._lbl.setAlignment(Qt.AlignCenter)
        self._lbl.setFixedSize(self._SIZE, self._SIZE)
        self._lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        lay.addWidget(self._lbl)

        self._refresh_style()

    def _refresh_style(self):
        color = DARK["accent"] if self._hovered else DARK["fg2"]
        border = DARK["accent"] if self._hovered else self._COLOR_OFF
        self._lbl.setStyleSheet(
            f"color: {color}; font-size: 9px; font-weight: 600; background: transparent; "
            f"border: 1px solid {border}; border-radius: {self._SIZE // 2}px;"
        )

    def enterEvent(self, event):
        self._hovered = True
        self._refresh_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._refresh_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self._popup is not None:
            self._popup.close()
            self._popup = None
        else:
            self._show_popup()
        super().mousePressEvent(event)

    def _show_popup(self):
        popup = QWidget(None, Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        popup.setAttribute(Qt.WA_TranslucentBackground)
        popup.setAttribute(Qt.WA_DeleteOnClose)
        popup.destroyed.connect(self._on_popup_destroyed)

        outer = QFrame(popup)
        outer.setObjectName("infoPopup")
        outer.setStyleSheet(
            "QFrame#infoPopup {"
            f"  background-color: {DARK['popup_bg']};"
            f"  border: 1px solid {accent_rgba(0.40)};"
            "  border-radius: 8px;"
            "}"
        )
        v = QVBoxLayout(outer)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(0)

        top_line = QFrame()
        top_line.setFixedHeight(2)
        top_line.setStyleSheet(f"background: {DARK['accent']}; border: none; border-radius: 1px;")
        v.addWidget(top_line)

        spacer = QWidget()
        spacer.setFixedHeight(8)
        spacer.setStyleSheet("background: transparent;")
        v.addWidget(spacer)

        msg = QLabel(self._text)
        msg.setWordWrap(True)
        msg.setFixedWidth(self._POPUP_W - 32)
        msg.setStyleSheet(
            f"color: {DARK['fg']}; font-size: 9pt;"
            "background: transparent; border: none; line-height: 150%;"
        )
        v.addWidget(msg)

        outer.adjustSize()
        popup.resize(outer.size())

        gpos_tr = self.mapToGlobal(self.rect().topRight())
        gpos_tl = self.mapToGlobal(self.rect().topLeft())
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        x = gpos_tr.x() + 6
        y = gpos_tr.y() - popup.height() // 2
        if x + popup.width() > screen.right():
            x = gpos_tl.x() - popup.width() - 6
        if y + popup.height() > screen.bottom():
            y = screen.bottom() - popup.height() - 4
        if y < screen.top():
            y = screen.top() + 4
        popup.move(x, y)
        popup.show()
        self._popup = popup

    def _on_popup_destroyed(self):
        self._popup = None

    def hideEvent(self, event):
        if self._popup is not None:
            self._popup.close()
        super().hideEvent(event)

    def closeEvent(self, event):
        if self._popup is not None:
            self._popup.close()
        super().closeEvent(event)


class _AntiSpySignals(QObject):
    done = Signal(bool)
