import sys
from typing import Optional, Union

from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QApplication,
    QMessageBox, QLineEdit, QScrollBar,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QObject, QEvent
from PySide6.QtGui import QColor, QFont, QPalette, QIcon

from qfluentwidgets import IconWidget, FluentIconBase, FluentIcon as FIF
from .constants import DARK, IS_LIGHT_THEME, accent_rgba


_C = DARK

GLOBAL_QSS = f"""
/* ── Base ── */
QWidget {{
    color: {_C['fg']};
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
    background: transparent;
}}
QDialog {{
    background: transparent;
}}
QMenu, QToolTip {{
    background-color: {_C['bg']};
}}
QFrame#toolbar {{
    background-color: {_C['toolbar_bg']};
}}
QFrame#searchBar {{
    background-color: {_C['searchbar_bg']};
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: transparent;
    width: 14px;
    border: none;
    margin: 2px 2px 2px 0;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 14px;
    border: none;
    margin: 0 2px 2px 2px;
}}
QScrollBar::handle:vertical {{
    background: {_C['scrollbar_handle']};
    border-radius: 3px;
    min-height: 32px;
    margin: 0 5px;
}}
QScrollBar::handle:horizontal {{
    background: {_C['scrollbar_handle']};
    border-radius: 3px;
    min-width: 32px;
    margin: 5px 0;
}}
QScrollBar::handle:vertical:hover {{
    background: {accent_rgba(0.70)};
    border-radius: 4px;
    margin: 0 2px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {accent_rgba(0.70)};
    border-radius: 4px;
    margin: 2px 0;
}}
QScrollBar::handle:vertical:pressed,
QScrollBar::handle:horizontal:pressed {{
    background: {accent_rgba(0.95)};
}}
QScrollBar:vertical:hover,
QScrollBar:horizontal:hover {{
    background: {_C['scrollbar_track_hover']};
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    width: 0; height: 0; background: none; border: none;
}}
QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
}}

/* Table & Header */
QTableWidget, QTreeWidget {{
    background-color: {_C['table_bg']};
    alternate-background-color: {_C['table_alt_bg']};
    color: {_C['fg']};
    gridline-color: {_C['grid_line']};
    border: 1px solid {_C['border_soft']};
    selection-background-color: {_C['sel_bg']};
    selection-color: {_C['sel_fg']};
}}
QHeaderView::section {{
    background-color: {_C['header_bg']};
    color: {_C['fg2']};
    border: none;
    border-bottom: 1px solid {_C['border_soft']};
    padding: 4px 8px;
    font-weight: bold;
}}

/* Input fields */
QLineEdit {{
    background-color: {_C['bg2']};
    color: {_C['fg']};
    border: 1px solid {_C['border']};
    border-radius: 4px;
    padding: 4px 8px;
}}
QLineEdit:focus {{
    border: 1px solid {_C['accent']};
}}
QTextEdit, QPlainTextEdit {{
    background-color: {_C['table_bg']};
    color: {_C['fg']};
    border: 1px solid {_C['border_soft']};
}}
"""

def apply_global_style(app: QApplication):
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_QSS)

    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(_C["bg"]))
    pal.setColor(QPalette.WindowText,      QColor(_C["fg"]))
    pal.setColor(QPalette.Base,            QColor(_C["bg2"]))
    pal.setColor(QPalette.AlternateBase,   QColor(_C["bg3"]))
    pal.setColor(QPalette.Text,            QColor(_C["fg"]))
    pal.setColor(QPalette.Button,          QColor(_C["btn_bg"]))
    pal.setColor(QPalette.ButtonText,      QColor(_C["btn_fg"]))
    pal.setColor(QPalette.Highlight,       QColor(_C["sel_bg"]))
    pal.setColor(QPalette.HighlightedText, QColor(_C["sel_fg"]))
    pal.setColor(QPalette.ToolTipBase,     QColor(_C["bg2"]))
    pal.setColor(QPalette.ToolTipText,     QColor(_C["fg"]))
    app.setPalette(pal)


class HOTSButton(QPushButton):

    def __init__(self, icon: Union[str, FluentIconBase, QIcon], icon_color: str, label: str, parent=None, accent: bool = False):
        super().__init__(parent)
        self._icon       = icon
        self._icon_color = icon_color
        self._label      = label
        self._accent     = accent
        self._glow_alpha = 0

        self._build_ui()
        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)
        self.setFixedHeight(42)
        self.setFocusPolicy(Qt.NoFocus)

        self._anim = QPropertyAnimation(self, b"glowAlpha", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        self._apply_base_style()

    def _get_glow(self) -> int:
        return self._glow_alpha

    def _set_glow(self, value: int):
        self._glow_alpha = value
        self._update_style()

    glowAlpha = Property(int, _get_glow, _set_glow)

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 14, 0)
        layout.setSpacing(8)

        if isinstance(self._icon, str):
            self._ico_lbl = QLabel(self._icon)
            self._ico_lbl.setFrameShape(QFrame.NoFrame)
            self._ico_lbl.setStyleSheet(
                f"color: {self._icon_color}; font-size: 19px; background: transparent; border: none; outline: none;"
            )
            self._ico_lbl.setAlignment(Qt.AlignCenter)
        else:
            self._ico_lbl = IconWidget(self._icon, self)
            self._ico_lbl.setFixedSize(18, 18)

        self._ico_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(self._ico_lbl)

        self._txt_lbl = QLabel(self._label)
        self._txt_lbl.setFrameShape(QFrame.NoFrame)
        self._txt_lbl.setStyleSheet(
            f"color: {DARK['fg']}; font-size: 9pt; background: transparent; border: none; outline: none;"
        )
        self._txt_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(self._txt_lbl)
        layout.addStretch()

    def _apply_base_style(self):
        if self._accent:
            base_bg     = accent_rgba(0.28)
            base_border = accent_rgba(0.55)
            pressed_bg  = accent_rgba(0.45)
            txt_color   = "#ffffff"
            weight      = "font-weight: 600;"
        else:
            r, g, b     = self._parse_rgb(self._icon_color)
            base_bg     = f"rgba({r},{g},{b},18)"
            base_border = f"rgba({r},{g},{b},55)"
            pressed_bg  = f"rgba({r},{g},{b},70)"
            txt_color   = DARK['fg']
            weight      = ""

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {base_bg};
                border: 1px solid {base_border};
                border-radius: 6px;
                outline: none;
            }}
            QPushButton:pressed {{
                background-color: {pressed_bg};
            }}
        """)
        self._txt_lbl.setStyleSheet(
            f"color: {txt_color}; font-size: 9pt; {weight} background: transparent; border: none; outline: none;"
        )
        self._update_icon_dynamic_color()

    def _update_style(self):
        a = self._glow_alpha
        if self._accent:
            opacity   = 0.28 + a / 255 * 0.22
            border_op = 0.55 + a / 255 * 0.35
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {accent_rgba(round(opacity, 2))};
                    border: 1px solid {accent_rgba(round(border_op, 2))};
                    border-radius: 6px;
                    outline: none;
                }}
                QPushButton:pressed {{
                    background-color: {accent_rgba(0.50)};
                }}
            """)
        else:
            r, g, b   = self._parse_rgb(self._icon_color)
            bg_op     = 18 + int(a * 0.14)
            border_op = 55 + int(a * 0.25)
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba({r},{g},{b},{bg_op});
                    border: 1px solid rgba({r},{g},{b},{border_op});
                    border-radius: 6px;
                    outline: none;
                }}
                QPushButton:pressed {{
                    background-color: rgba({r},{g},{b},{min(bg_op + 20, 255)});
                }}
            """)
        
        self._update_icon_dynamic_color()

    def _update_icon_dynamic_color(self):
        if not hasattr(self, '_ico_lbl'):
            return
        
        a = self._glow_alpha
        if self._accent:
            color = QColor("#ffffff")
        else:
            if a > 160:
                bright = min(255, int(180 + a * 0.29))
                color = QColor(bright, bright, bright)
            else:
                color = QColor(self._icon_color)

        if isinstance(self._ico_lbl, QLabel):
            self._ico_lbl.setStyleSheet(
                f"color: {color.name()}; font-size: 19px; background: transparent; border: none; outline: none;"
            )
        elif isinstance(self._ico_lbl, IconWidget):
            if isinstance(self._icon, FluentIconBase):
                self._ico_lbl.setIcon(self._icon.icon(color=color))

    def _parse_rgb(self, hex_color: str):
        try:
            hex_c = hex_color.lstrip("#")
            return int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)
        except Exception:
            return 255, 255, 255

    def enterEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self._glow_alpha)
        self._anim.setEndValue(255)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self._glow_alpha)
        self._anim.setEndValue(0)
        self._anim.start()
        super().leaveEvent(event)

    def set_accent(self, active: bool):
        self._accent = active
        self._apply_base_style()
        if self._glow_alpha > 0:
            self._update_style()

    def set_icon(self, icon: Union[str, FluentIconBase, QIcon], color: Optional[str] = None):
        self._icon = icon
        if color is not None:
            self._icon_color = color
        self._apply_base_style()
        if self._glow_alpha > 0:
            self._update_style()

    def fit_to_content(self, padding: int = 8):
        self.setFixedWidth(self.layout().sizeHint().width() + padding)

    def set_label(self, text: str):
        self._txt_lbl.setText(text)


class HOTSDialog(QDialog):

    def __init__(self, parent: Optional[QWidget] = None, title: str = "HOTS",
                 min_width: int = 340, min_height: int = 200):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setWindowTitle(title)
        self.setMinimumSize(min_width, min_height)
        self.setStyleSheet("QDialog { background: transparent; }")
        
        self._title_text = title
        self._build_frame()

    def _build_frame(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(1, 1, 1, 1)
        root.setSpacing(0)

        self.custom_title_bar = QWidget()
        self.custom_title_bar.setFixedHeight(45)
        self.custom_title_bar.setStyleSheet("background: rgba(0,0,0,0.01);")
        
        tb_layout = QHBoxLayout(self.custom_title_bar)
        tb_layout.setContentsMargins(16, 0, 10, 0)
        
        self.title_label = QLabel(self._title_text)
        self.title_label.setStyleSheet(
            f"color: {DARK['accent']}; font-size: 11pt; background: transparent;"
        )
        tb_layout.addWidget(self.title_label)
        tb_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                color: {DARK['fg2']}; font-size: 11px; border: none; border-radius: 4px; background: transparent;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 0, 0, 0.7); color: white;
            }}
        """)
        close_btn.clicked.connect(self.reject)
        tb_layout.addWidget(close_btn)
        
        root.addWidget(self.custom_title_bar)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"background-color: {DARK['accent']}; border: none;")
        root.addWidget(sep)

        self.body = QWidget()
        self.body.setStyleSheet(
            f"background-color: {DARK['dialog_body_bg']}; "
            f"border-bottom-left-radius: 6px; border-bottom-right-radius: 6px;"
        )
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        root.addWidget(self.body, 1)

    def set_title(self, title: str):
        self._title_text = title
        if hasattr(self, 'title_label'):
            self.title_label.setText(title)
        self.setWindowTitle(title)

    def center_on_parent(self):
        if self.parent():
            top = self.parent().window()
            p = top.frameGeometry()
            self.move(p.center() - self.rect().center())
        else:
            screen = QApplication.primaryScreen().geometry()
            self.move(screen.center() - self.rect().center())

    def showEvent(self, event):
        super().showEvent(event)
        try:
            hwnd = int(self.winId())
            _dwm_dark_titlebar(hwnd, dark=not IS_LIGHT_THEME)
            enable_rounded_corners(hwnd)
            _dwm_mica_dialog(hwnd, dark=not IS_LIGHT_THEME)
        except Exception:
            pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() < 45:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            self._drag_pos = None

    def mouseMoveEvent(self, event):
        if getattr(self, '_drag_pos', None) is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    @staticmethod
    def info(parent, title: str, message: str):
        d = _MsgDialog(parent, title, message, "info")
        d.exec()

    @staticmethod
    def error(parent, title: str, message: str):
        d = _MsgDialog(parent, title, message, "error")
        d.exec()

    @staticmethod
    def ask(parent, title: str, message: str) -> bool:
        d = _MsgDialog(parent, title, message, "ask")
        return d.exec() == QDialog.Accepted

    @staticmethod
    def restart_prompt(parent, title: str, message: str) -> bool:
        d = _MsgDialog(parent, title, message, "restart")
        return d.exec() == QDialog.Accepted


class HOTSPage(QWidget):

    def __init__(self, object_name: str, icon: FluentIconBase, title: str,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName(object_name)
        self._title_text = title
        self._icon = icon
        self._build_frame()

    def _build_frame(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(0)

        header = QHBoxLayout()
        header.setSpacing(10)

        ico = IconWidget(self._icon)
        ico.setFixedSize(22, 22)
        ico.setIcon(self._icon.icon(color=QColor(DARK["accent"])))
        header.addWidget(ico)

        self.title_label = QLabel(self._title_text)
        self.title_label.setStyleSheet(
            f"color: {DARK['accent']}; font-size: 14pt; font-weight: 600; background: transparent;"
        )
        header.addWidget(self.title_label)
        header.addStretch()
        root.addLayout(header)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"background-color: {accent_rgba(0.35)}; border: none;")
        root.addWidget(sep)
        root.addSpacing(12)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        root.addLayout(self.content_layout, 1)

    def set_title(self, title: str):
        self._title_text = title
        self.title_label.setText(title)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_content()

    def refresh_content(self):
        pass


class _MsgDialog(HOTSDialog):
    ICONS = {
        "info":    (FIF.INFO,   "#60c8ff"),
        "error":   (FIF.INFO,   DARK["red"]),
        "ask":     (FIF.HELP,   DARK["accent"]),
        "restart": (FIF.SYNC,   DARK["accent"]),
    }

    def __init__(self, parent, title, message, kind):
        super().__init__(parent, title, min_width=360, min_height=160)
        icon_fif, icon_color = self.ICONS.get(kind, (FIF.INFO, "#60c8ff"))

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(24, 18, 24, 12)
        cl.setSpacing(12)

        row = QHBoxLayout()
        row.setSpacing(12)
        ico = IconWidget(icon_fif)
        ico.setFixedSize(22, 22)
        ico.setIcon(icon_fif.icon(color=QColor(icon_color)))
        row.addWidget(ico, 0, Qt.AlignTop)

        msg = QLabel(message)
        msg.setWordWrap(True)
        msg.setStyleSheet(f"color: {DARK['fg']}; background: transparent;")
        row.addWidget(msg, 1)
        cl.addLayout(row)
        cl.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        if kind == "ask":
            from .i18n import T
            yes = HOTSButton(FIF.ACCEPT, "#4ec94e", T("btn_ok"), accent=True)
            yes.setFixedWidth(90)
            yes.clicked.connect(self.accept)
            btn_row.addWidget(yes)
            no = HOTSButton(FIF.CLOSE, DARK["red"], T("btn_cancel"))
            no.setFixedWidth(90)
            no.clicked.connect(self.reject)
            btn_row.addWidget(no)
        elif kind == "restart":
            from .i18n import T
            later = HOTSButton(FIF.CLOSE, DARK["fg2"], T("btn_later"))
            later.fit_to_content()
            later.clicked.connect(self.reject)
            btn_row.addWidget(later)
            now = HOTSButton(FIF.SYNC, DARK["accent"], T("btn_restart_now"), accent=True)
            now.fit_to_content()
            now.clicked.connect(self.accept)
            btn_row.addWidget(now)
        else:
            from .i18n import T
            ok = HOTSButton(FIF.ACCEPT, "#60c8ff", T("btn_ok"))
            ok.setFixedWidth(90)
            ok.clicked.connect(self.accept)
            btn_row.addWidget(ok)

        btn_row.addStretch()

        cl.addLayout(btn_row)
        self.body_layout.addWidget(content)
        self.adjustSize()
        self.center_on_parent()


class HOTSContextMenu(QWidget):
    _ITEM_H   = 36
    _SEP_H    = 9
    _PAD_V    = 6
    _PAD_H    = 6
    _MIN_W    = 190

    def __init__(self, parent, items: list):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)

        self._items    = items
        self._hovered  = -1
        self._callbacks: list = []

        self._build()

    def _build(self):
        from PySide6.QtWidgets import QVBoxLayout as _QV, QFrame as _QF
        outer = _QV(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._bg = _QF(self)
        self._bg.setObjectName("ctxBg")
        self._bg.setStyleSheet(
            f"QFrame#ctxBg {{"
            f"  background-color: {DARK['popup_bg']};"
            f"  border: 1px solid {DARK['border_soft2']};"
            f"  border-radius: 10px;"
            f"}}"
        )
        inner = _QV(self._bg)
        inner.setContentsMargins(self._PAD_H, self._PAD_V, self._PAD_H, self._PAD_V)
        inner.setSpacing(0)

        self._row_widgets: list = []
        real_idx = 0

        for entry in self._items:
            if entry is None:
                sep = QFrame()
                sep.setFixedHeight(1)
                sep.setStyleSheet(f"background: {DARK['border_soft2']}; border: none; margin: 4px 6px;")
                inner.addWidget(sep)
                self._row_widgets.append(None)
            else:
                icon_ch, icon_color, label, cb = entry
                row = _CtxRow(icon_ch, icon_color, label, real_idx, self)
                row.hovered.connect(self._on_hover)
                row.clicked.connect(self._on_click)
                inner.addWidget(row)
                self._row_widgets.append(row)
                self._callbacks.append(cb)
                real_idx += 1

        outer.addWidget(self._bg)
        self.adjustSize()

    def popup(self, global_pos):
        from PySide6.QtWidgets import QApplication as _QApp
        self.adjustSize()
        screen = _QApp.primaryScreen().availableGeometry()
        x = global_pos.x()
        y = global_pos.y()
        if x + self.width() > screen.right():
            x = screen.right() - self.width() - 4
        if y + self.height() > screen.bottom():
            y = global_pos.y() - self.height()
        self.move(x, y)
        self.show()
        self.raise_()

        app = _QApp.instance()
        if app is not None:
            app.removeEventFilter(self)
            app.installEventFilter(self)

    def _on_hover(self, idx: int):
        self._hovered = idx

    def _on_click(self, idx: int):
        from PySide6.QtCore import QTimer as _QTimer
        cb = self._callbacks[idx]
        _QTimer.singleShot(0, lambda: self._finish_click(cb))

    def _finish_click(self, cb):
        from PySide6.QtWidgets import QApplication as _QApp
        app = _QApp.instance()
        if app is not None:
            app.removeEventFilter(self)
        self.hide()
        self.deleteLater()
        if cb:
            cb()

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        from PySide6.QtWidgets import QApplication as _QApp
        if event.type() == QEvent.Type.MouseButtonPress:
            try:
                gpos = event.globalPosition().toPoint()
            except AttributeError:
                try:
                    gpos = event.globalPos()
                except Exception:
                    return False
            try:
                if not self.geometry().contains(gpos):
                    app = _QApp.instance()
                    if app is not None:
                        app.removeEventFilter(self)
                    from PySide6.QtCore import QTimer as _QTimer
                    _QTimer.singleShot(0, self._close_outside_click)
            except Exception:
                pass
        return False

    def _close_outside_click(self):
        self.hide()
        self.deleteLater()

    def hideEvent(self, event):
        try:
            from PySide6.QtWidgets import QApplication as _QApp
            app = _QApp.instance()
            if app is not None:
                app.removeEventFilter(self)
        except Exception:
            pass
        super().hideEvent(event)


class _CtxRow(QWidget):
    from PySide6.QtCore import Signal as _Signal
    hovered = _Signal(int)
    clicked = _Signal(int)

    def __init__(self, icon_ch: str, icon_color: str, label: str, idx: int, parent=None):
        super().__init__(parent)
        self._idx        = idx
        self._icon_color = icon_color
        self._hov        = False
        self.setObjectName("ctxRow")
        self.setFixedHeight(36)
        self.setCursor(Qt.PointingHandCursor)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 14, 0)
        lay.setSpacing(10)

        self._ico = QLabel(icon_ch)
        self._ico.setFixedWidth(18)
        self._ico.setAlignment(Qt.AlignCenter)
        self._ico.setStyleSheet(
            f"color: {icon_color}; font-size: 14px; background: transparent; border: none;"
        )
        lay.addWidget(self._ico)

        self._lbl = QLabel(label)
        self._lbl.setStyleSheet(
            f"color: {DARK['fg']}; font-size: 10pt; background: transparent; border: none;"
        )
        lay.addWidget(self._lbl, 1)

        self._update_bg()

    def _update_bg(self):
        if self._hov:
            try:
                c = QColor(self._icon_color)
                r, g, b = c.red(), c.green(), c.blue()
                bg = f"rgba({r},{g},{b},0.13)"
                bd = f"rgba({r},{g},{b},0.35)"
            except Exception:
                bg, bd = DARK['panel_bg_alt'], DARK['border_soft2']
            self.setStyleSheet(
                f"QWidget#ctxRow {{ background-color: {bg}; border: 1px solid {bd}; border-radius: 6px; }}"
                f"QLabel {{ background: transparent; border: none; }}"
            )
            self._lbl.setStyleSheet(
                f"color: {DARK['fg']}; font-size: 10pt; font-weight: 600; background: transparent; border: none;"
            )
        else:
            self.setStyleSheet(
                f"QWidget#ctxRow {{ background: transparent; border: none; }}"
                f"QLabel {{ background: transparent; border: none; }}"
            )
            self._lbl.setStyleSheet(
                f"color: {DARK['fg']}; font-size: 10pt; background: transparent; border: none;"
            )

    def enterEvent(self, event):
        self._hov = True
        self._update_bg()
        self.hovered.emit(self._idx)

    def leaveEvent(self, event):
        self._hov = False
        self._update_bg()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._idx)


def attach_line_edit_context_menu(line_edit):
    from PySide6.QtCore import Qt as _Qt

    def _show(pos):
        from .i18n import T
        gpos = line_edit.mapToGlobal(pos)
        is_masked = line_edit.echoMode() != QLineEdit.Normal
        items = []
        if not is_masked:
            items.append(("✂", DARK['accent'], T("ctx_cut"),  line_edit.cut))
            items.append(("⧉", DARK['accent'], T("ctx_copy"), line_edit.copy))
        items.append(("📋", DARK['accent'], T("ctx_paste"), line_edit.paste))
        items.append(None)
        items.append(("▤", DARK['accent'], T("ctx_select_all"), line_edit.selectAll))
        menu = HOTSContextMenu(line_edit, items)
        line_edit._hots_ctx_menu = menu
        menu.popup(gpos)

    line_edit.setContextMenuPolicy(_Qt.CustomContextMenu)
    line_edit.customContextMenuRequested.connect(_show)


def attach_text_edit_context_menu(text_edit):
    from PySide6.QtCore import Qt as _Qt

    def _delete_selection():
        cursor = text_edit.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()

    def _show(pos):
        from .i18n import T
        gpos = text_edit.mapToGlobal(pos)
        items = [
            ("✂", DARK['accent'], T("ctx_cut"),        text_edit.cut),
            ("⧉", DARK['accent'], T("ctx_copy"),        text_edit.copy),
            ("📋", DARK['accent'], T("ctx_paste"),       text_edit.paste),
            ("✖", "#e05050",      T("ctx_delete"),      _delete_selection),
            None,
            ("▤", DARK['accent'], T("ctx_select_all"), text_edit.selectAll),
        ]
        menu = HOTSContextMenu(text_edit, items)
        text_edit._hots_ctx_menu = menu
        menu.popup(gpos)

    text_edit.setContextMenuPolicy(_Qt.CustomContextMenu)
    text_edit.customContextMenuRequested.connect(_show)


def h_separator() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background-color: {DARK['border']}; border: none;")
    return f


def v_separator() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.VLine)
    f.setFixedWidth(1)
    f.setStyleSheet(f"background-color: {DARK['border_soft2']}; border: none; margin: 4px 2px;")
    return f


def _dwm_dark_titlebar(hwnd: int, dark: bool = True) -> None:
    try:
        import ctypes
        val = ctypes.c_int(1 if dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd), ctypes.c_uint(20),
            ctypes.byref(val), ctypes.sizeof(val),
        )
    except Exception:
        pass


def _dwm_mica_dialog(hwnd: int, dark: bool = True) -> None:
    try:
        import ctypes, ctypes.wintypes
        build = sys.getwindowsversion().build

        if build >= 22000:
            class MARGINS(ctypes.Structure):
                _fields_ = [("left", ctypes.c_int), ("right", ctypes.c_int),
                            ("top",  ctypes.c_int), ("bottom", ctypes.c_int)]
            ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(
                ctypes.wintypes.HWND(hwnd),
                ctypes.byref(MARGINS(-1, -1, -1, -1))
            )
            if build >= 22621:
                val = ctypes.c_int(2)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.wintypes.HWND(hwnd), ctypes.c_uint(38),
                    ctypes.byref(val), ctypes.c_uint(ctypes.sizeof(val))
                )
            else:
                val = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.wintypes.HWND(hwnd), ctypes.c_uint(1029),
                    ctypes.byref(val), ctypes.c_uint(ctypes.sizeof(val))
                )
        else:
            class _ACCENT(ctypes.Structure):
                _fields_ = [("AccentState", ctypes.c_uint), ("AccentFlags", ctypes.c_uint),
                            ("GradientColor", ctypes.c_uint), ("AnimationId", ctypes.c_uint)]
            class _WCAD(ctypes.Structure):
                _fields_ = [("Attribute", ctypes.c_int), ("pData", ctypes.c_void_p),
                            ("ulDataSize", ctypes.c_ulong)]
            gradient_color = 0xB41A1A2A if dark else 0xCCF2F2F2
            accent = _ACCENT(4, 0, gradient_color, 0)
            data   = _WCAD(19, ctypes.cast(ctypes.byref(accent), ctypes.c_void_p),
                           ctypes.sizeof(accent))
            ctypes.windll.user32.SetWindowCompositionAttribute(
                ctypes.wintypes.HWND(hwnd), ctypes.byref(data)
            )
    except Exception:
        pass


def enable_rounded_corners(hwnd: int):
    try:
        import ctypes
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd), ctypes.c_uint(33),
            ctypes.byref(ctypes.c_int(2)), ctypes.sizeof(ctypes.c_int())
        )
    except Exception:
        pass


def enable_acrylic(hwnd: int, dark: bool = True) -> None:
    try:
        import ctypes, ctypes.wintypes
        build = sys.getwindowsversion().build
        if build >= 22621:
            val = ctypes.c_int(2)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.wintypes.HWND(hwnd), ctypes.c_uint(38),
                ctypes.byref(val), ctypes.c_uint(ctypes.sizeof(val))
            )
        elif build >= 22000:
            val = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.wintypes.HWND(hwnd), ctypes.c_uint(1029),
                ctypes.byref(val), ctypes.c_uint(ctypes.sizeof(val))
            )
        else:
            class _ACCENT(ctypes.Structure):
                _fields_ = [("AccentState", ctypes.c_uint), ("AccentFlags", ctypes.c_uint),
                            ("GradientColor", ctypes.c_uint), ("AnimationId", ctypes.c_uint)]
            class _WCAD(ctypes.Structure):
                _fields_ = [("Attribute", ctypes.c_int), ("pData", ctypes.c_void_p),
                            ("ulDataSize", ctypes.c_ulong)]
            gradient_color = 0xB41A1A2A if dark else 0xCCF2F2F2
            accent = _ACCENT(4, 0, gradient_color, 0)
            data   = _WCAD(19, ctypes.cast(ctypes.byref(accent), ctypes.c_void_p),
                           ctypes.sizeof(accent))
            ctypes.windll.user32.SetWindowCompositionAttribute(
                ctypes.wintypes.HWND(hwnd), ctypes.byref(data)
            )
    except Exception:
        pass

class NoScrollbarContextMenuFilter(QObject):

    def eventFilter(self, obj, event):
        if event.type() == QEvent.ContextMenu and isinstance(obj, QScrollBar):
            return True
        return super().eventFilter(obj, event)
