import sys
import time
import ctypes
import weakref
from typing import Optional, Union

from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QApplication, QLineEdit,
    QScrollBar, QCheckBox, QRadioButton, QStyle, QStyleOptionButton, QAbstractScrollArea, QAbstractItemView,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QObject, QEvent, QTimer, QRectF, QVariantAnimation, QSize as _QSize
from PySide6.QtGui import QColor, QPalette, QIcon, QCursor, QPainter, QPen

import shiboken6
from .constants import DARK, IS_LIGHT_THEME, accent_rgba
from .bg_tasks import is_shutting_down, register_wakeup
from .icons import FIF, AppIcon, make_qicon
from .ui_parts import IconWidget, IndeterminateProgressRing, TransparentToolButton


def colored_svg_icon(fif_icon, color, theme=None, sizes=None) -> QIcon:
    """Coloured QIcon from an FIF icon. `theme` is unused, kept for old call sites."""
    return make_qicon(fif_icon, color, sizes)


_open_tip_popups: list = []

def _close_all_open_tip_popups() -> None:
    for popup in list(_open_tip_popups):
        try:
            popup.close()
        except Exception:
            pass

register_wakeup(_close_all_open_tip_popups)

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

class _FluentTipFilter(QObject):

    _SHOW_DELAY_MS = 900

    def __init__(self, target: QWidget, text: str, width: Optional[int] = None,
                 side: str = "bottom", delay_ms: Optional[int] = None):
        super().__init__(target)
        self._target = target
        self._text = text
        self._width = width
        # side: "bottom" (default, tip below the element) or "right" (to the right, vertically
        # centred - for the vertical nav rail)
        self._side = side
        self._delay_ms = delay_ms if delay_ms is not None else self._SHOW_DELAY_MS
        self._popup: Optional[QWidget] = None
        self._show_timer = QTimer(self)
        self._show_timer.setSingleShot(True)
        self._show_timer.timeout.connect(self._show)
        target.installEventFilter(self)

        self_ref = weakref.ref(self)

        def _on_target_destroyed(*_args, _ref=self_ref):
            obj = _ref()
            if obj is not None:
                obj._handle_target_destroyed()

        target.destroyed.connect(_on_target_destroyed)

    def _handle_target_destroyed(self, *_args):
        self._show_timer.stop()
        self._hide()

    def set_text(self, text: str):
        self._text = text
        if not text:
            self._show_timer.stop()
            self._hide()

    def eventFilter(self, obj, event):
        if obj is self._target:
            et = event.type()
            if et == QEvent.Enter:
                if self._text:
                    self._show_timer.start(self._delay_ms)
            elif et in (QEvent.Leave, QEvent.Hide, QEvent.MouseButtonPress):
                self._show_timer.stop()
                self._hide()
        return False

    def _show(self):
        if self._popup is not None or not self._text:
            return
        if is_shutting_down():
            return

        popup = QWidget(None, Qt.ToolTip | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        popup.setAttribute(Qt.WA_TranslucentBackground)
        popup.setAttribute(Qt.WA_TransparentForMouseEvents)
        popup.setAttribute(Qt.WA_ShowWithoutActivating)
        popup.setAttribute(Qt.WA_DeleteOnClose)

        self_ref = weakref.ref(self)

        def _on_popup_destroyed(*_args, _ref=self_ref, _popup=popup):
            obj = _ref()
            if obj is not None:
                obj._handle_popup_destroyed(_popup)
            else:
                _open_tip_popups[:] = [p for p in _open_tip_popups if p is not _popup]

        popup.destroyed.connect(_on_popup_destroyed)

        outer = QFrame(popup)
        outer.setObjectName("fluentTip")
        outer.setStyleSheet(
            "QFrame#fluentTip {"
            f"  background-color: {_C['popup_bg']};"
            f"  border: 1px solid {accent_rgba(0.40)};"
            "  border-radius: 8px;"
            "}"
        )
        v = QVBoxLayout(outer)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(0)

        top_line = QFrame()
        top_line.setFixedHeight(2)
        top_line.setStyleSheet(f"background: {_C['accent']}; border: none; border-radius: 1px;")
        v.addWidget(top_line)

        spacer = QWidget()
        spacer.setFixedHeight(6)
        spacer.setStyleSheet("background: transparent;")
        v.addWidget(spacer)

        msg = QLabel(self._text)
        msg.setStyleSheet(
            f"color: {_C['fg']}; font-size: 9pt; background: transparent; "
            "border: none; line-height: 150%;"
        )
        if self._width:
            msg.setWordWrap(True)
            msg.setFixedWidth(self._width)
        v.addWidget(msg)

        for w in (top_line, spacer, msg, outer):
            w.ensurePolished()
        if msg.wordWrap():
            msg.setMinimumHeight(msg.heightForWidth(msg.width()) + 2)
        outer.adjustSize()
        popup.resize(outer.size())

        screen = QApplication.primaryScreen().availableGeometry()
        if self._side == "right":
            gpos_tr = self._target.mapToGlobal(self._target.rect().topRight())
            x = gpos_tr.x() + 8
            y = gpos_tr.y() + (self._target.height() - popup.height()) // 2
            if x + popup.width() > screen.right():
                x = screen.right() - popup.width() - 4
            y = max(screen.top() + 4, min(y, screen.bottom() - popup.height() - 4))
        else:
            gpos_bl = self._target.mapToGlobal(self._target.rect().bottomLeft())
            x = gpos_bl.x()
            y = gpos_bl.y() + 6
            if x + popup.width() > screen.right():
                x = screen.right() - popup.width() - 4
            if y + popup.height() > screen.bottom():
                y = gpos_bl.y() - popup.height() - 6 - self._target.height()
        popup.move(x, y)
        popup.show()
        self._popup = popup
        _open_tip_popups.append(popup)

    def _hide(self):
        if self._popup is not None:
            self._popup.close()

    def _handle_popup_destroyed(self, popup):
        if self._popup is popup:
            self._popup = None
        _open_tip_popups[:] = [p for p in _open_tip_popups if p is not popup]

def attach_fluent_tip(widget: QWidget, text: str, width: Optional[int] = None,
                      side: str = "bottom", delay_ms: Optional[int] = None) -> _FluentTipFilter:
    existing = getattr(widget, "_fluent_tip_filter", None)
    if isinstance(existing, _FluentTipFilter):
        existing.set_text(text)
        if width is not None:
            existing._width = width
        existing._side = side
        if delay_ms is not None:
            existing._delay_ms = delay_ms
        return existing
    filt = _FluentTipFilter(widget, text, width, side, delay_ms)
    widget._fluent_tip_filter = filt
    return filt

class _FluentTableTipFilter(QObject):
    _SHOW_DELAY_MS = 400

    def __init__(self, table):
        super().__init__(table)
        self._table = table
        self._viewport = table.viewport()
        self._viewport.setMouseTracking(True)
        table.setMouseTracking(True)
        self._viewport.installEventFilter(self)
        self._popup = None
        self._current_item = None
        self._pending_text = ""
        self._show_timer = QTimer(self)
        self._show_timer.setSingleShot(True)
        self._show_timer.timeout.connect(self._show)

        self_ref = weakref.ref(self)

        def _on_target_destroyed(*_args, _ref=self_ref):
            obj = _ref()
            if obj is not None:
                obj._handle_target_destroyed()

        table.destroyed.connect(_on_target_destroyed)

    def _handle_target_destroyed(self, *_args):
        self._show_timer.stop()
        self._hide()

    def eventFilter(self, obj, event):
        if obj is self._viewport:
            et = event.type()
            if et == QEvent.ToolTip:

                return True
            if et == QEvent.MouseMove:
                pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
                item = self._table.itemAt(pos)
                if item is not self._current_item:
                    self._current_item = item
                    self._show_timer.stop()
                    self._hide()
                    text = item.toolTip() if item is not None else ""
                    if text:
                        self._pending_text = text
                        self._show_timer.start(self._SHOW_DELAY_MS)
            elif et in (QEvent.Leave, QEvent.MouseButtonPress, QEvent.Wheel):
                self._current_item = None
                self._show_timer.stop()
                self._hide()
        return False

    def _show(self):
        if self._popup is not None or not self._pending_text:
            return
        if is_shutting_down():
            return

        popup = QWidget(None, Qt.ToolTip | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        popup.setAttribute(Qt.WA_TranslucentBackground)
        popup.setAttribute(Qt.WA_TransparentForMouseEvents)
        popup.setAttribute(Qt.WA_ShowWithoutActivating)
        popup.setAttribute(Qt.WA_DeleteOnClose)

        self_ref = weakref.ref(self)

        def _on_popup_destroyed(*_args, _ref=self_ref, _popup=popup):
            obj = _ref()
            if obj is not None:
                obj._handle_popup_destroyed(_popup)
            else:
                _open_tip_popups[:] = [p for p in _open_tip_popups if p is not _popup]

        popup.destroyed.connect(_on_popup_destroyed)

        outer = QFrame(popup)
        outer.setObjectName("fluentTip")
        outer.setStyleSheet(
            "QFrame#fluentTip {"
            f"  background-color: {_C['popup_bg']};"
            f"  border: 1px solid {accent_rgba(0.40)};"
            "  border-radius: 8px;"
            "}"
        )
        v = QVBoxLayout(outer)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(0)

        top_line = QFrame()
        top_line.setFixedHeight(2)
        top_line.setStyleSheet(f"background: {_C['accent']}; border: none; border-radius: 1px;")
        v.addWidget(top_line)

        spacer = QWidget()
        spacer.setFixedHeight(6)
        spacer.setStyleSheet("background: transparent;")
        v.addWidget(spacer)

        msg = QLabel(self._pending_text)
        msg.setStyleSheet(
            f"color: {_C['fg']}; font-size: 9pt; background: transparent; "
            "border: none; line-height: 150%;"
        )
        v.addWidget(msg)

        for w in (top_line, spacer, msg, outer):
            w.ensurePolished()
        if msg.wordWrap():
            msg.setMinimumHeight(msg.heightForWidth(msg.width()) + 2)
        outer.adjustSize()
        popup.resize(outer.size())

        gpos = QCursor.pos()
        screen = QApplication.primaryScreen().availableGeometry()
        x = gpos.x() + 14
        y = gpos.y() + 18
        if x + popup.width() > screen.right():
            x = screen.right() - popup.width() - 4
        if y + popup.height() > screen.bottom():
            y = gpos.y() - popup.height() - 10
        popup.move(x, y)
        popup.show()
        self._popup = popup
        _open_tip_popups.append(popup)

    def _hide(self):
        if self._popup is not None:
            self._popup.close()

    def _handle_popup_destroyed(self, popup):
        if self._popup is popup:
            self._popup = None
        _open_tip_popups[:] = [p for p in _open_tip_popups if p is not popup]

def attach_fluent_table_tip(table) -> _FluentTableTipFilter:
    existing = getattr(table, "_fluent_table_tip_filter", None)
    if isinstance(existing, _FluentTableTipFilter):
        return existing
    filt = _FluentTableTipFilter(table)
    table._fluent_table_tip_filter = filt
    return filt

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

    def __init__(self, icon: Union[str, AppIcon, QIcon], icon_color: str, label: str, parent=None,
                 accent: bool = False, glyph_color: Optional[str] = None, icon_size: int = 18,
                 radius: int = 6, h_margins: tuple = (12, 14)):
        super().__init__(parent)
        self._icon       = icon
        self._icon_color = icon_color

        self._glyph_color = glyph_color
        self._label      = label
        self._accent     = accent
        self._glow_alpha = 0
        self._icon_size  = icon_size
        self._radius     = radius
        self._h_margins  = h_margins

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
        layout.setContentsMargins(self._h_margins[0], 0, self._h_margins[1], 0)
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
            self._ico_lbl.setFixedSize(self._icon_size, self._icon_size)

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
                border-radius: {self._radius}px;
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
                    border-radius: {self._radius}px;
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
                    border-radius: {self._radius}px;
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
                color = QColor(self._glyph_color or self._icon_color)

        if isinstance(self._ico_lbl, QLabel):
            self._ico_lbl.setStyleSheet(
                f"color: {color.name()}; font-size: 19px; background: transparent; border: none; outline: none;"
            )
        elif isinstance(self._ico_lbl, IconWidget):
            if isinstance(self._icon, AppIcon):

                self._ico_lbl.setIcon(colored_svg_icon(self._icon, color, sizes=(self._icon_size,)))

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

    def set_icon(self, icon: Union[str, AppIcon, QIcon], color: Optional[str] = None,
                 glyph_color: Optional[str] = None):
        self._icon = icon
        if color is not None:
            self._icon_color = color
        if glyph_color is not None:
            self._glyph_color = glyph_color
        self._apply_base_style()
        if self._glow_alpha > 0:
            self._update_style()

    def fit_to_content(self, padding: int = 8, min_width: int = 0):
        width = self.layout().sizeHint().width() + padding
        if min_width:
            width = max(width, min_width)
        self.setFixedWidth(width)

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

class EqualHeight(QObject):

    def __init__(self, source: QWidget, targets):
        super().__init__(source)
        self._targets = targets
        source.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Resize:
            h = obj.height()
            if h > 0:
                for w in self._targets:
                    if shiboken6.isValid(w) and (w.minimumHeight() != h or w.maximumHeight() != h):
                        w.setFixedHeight(h)
        return False


class HOTSPage(QWidget):

    _MIN_BUSY_VISIBLE_S = 1.0
    _refresh_on_show = True

    def __init__(self, object_name: str, icon: AppIcon, title: str,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName(object_name)
        self._title_text = title
        self._icon = icon
        self._build_frame()

    def _build_frame(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 14, 24, 14)
        root.setSpacing(0)

        header = QHBoxLayout()
        header.setSpacing(10)

        ico = IconWidget(self._icon)
        ico.setFixedSize(22, 22)
        ico.setIcon(colored_svg_icon(self._icon, QColor(DARK["accent"]), sizes=(22,)))
        header.addWidget(ico)

        self.title_label = QLabel(self._title_text)
        self.title_label.setStyleSheet(
            f"color: {DARK['accent']}; font-size: 14pt; font-weight: 600; background: transparent;"
        )
        header.addWidget(self.title_label)
        header.addStretch()

        self._busy_count = 0
        self._busy_started_at = 0.0
        self._busy_spinner = None
        self._busy_label = None
        if IndeterminateProgressRing is not None:
            self._busy_spinner = IndeterminateProgressRing()
            self._busy_spinner.setFixedSize(16, 16)
            self._busy_spinner.setStrokeWidth(2)
            self._busy_spinner.setVisible(False)
            header.addWidget(self._busy_spinner, 0, Qt.AlignVCenter)

        from .i18n import T
        self._busy_label = QLabel(T("priv_op_working"))
        self._busy_label.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent;")
        self._busy_label.setVisible(False)
        header.addWidget(self._busy_label, 0, Qt.AlignVCenter)

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

    def begin_busy(self):
        self._busy_count += 1
        if self._busy_count == 1:
            self._busy_started_at = time.monotonic()
            if self._busy_spinner is not None and shiboken6.isValid(self._busy_spinner):
                self._busy_spinner.setVisible(True)
            if self._busy_label is not None and shiboken6.isValid(self._busy_label):
                self._busy_label.setVisible(True)

    def end_busy(self):
        self._busy_count = max(0, self._busy_count - 1)
        if self._busy_count > 0:
            return
        remaining = self._MIN_BUSY_VISIBLE_S - (time.monotonic() - self._busy_started_at)
        if remaining > 0:
            QTimer.singleShot(int(remaining * 1000), self._hide_busy_indicator)
        else:
            self._hide_busy_indicator()

    def _hide_busy_indicator(self):
        if not shiboken6.isValid(self):
            return

        if self._busy_count != 0:
            return
        if self._busy_spinner is not None and shiboken6.isValid(self._busy_spinner):
            self._busy_spinner.setVisible(False)
        if self._busy_label is not None and shiboken6.isValid(self._busy_label):
            self._busy_label.setVisible(False)

    def showEvent(self, event):
        super().showEvent(event)
        if self._refresh_on_show:
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

        ico = IconWidget(icon_fif)
        ico.setFixedSize(22, 22)
        ico.setIcon(colored_svg_icon(icon_fif, QColor(icon_color), sizes=(22,)))
        cl.addWidget(ico, 0, Qt.AlignHCenter)

        msg = QLabel(message)
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignCenter)
        msg.setStyleSheet(f"color: {DARK['fg']}; background: transparent;")
        cl.addWidget(msg)
        cl.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        if kind == "ask":
            from .i18n import T
            yes = HOTSButton(FIF.ACCEPT, "#4ec94e", T("btn_ok"), accent=True)
            yes.fit_to_content(min_width=90)
            yes.clicked.connect(self.accept)
            btn_row.addWidget(yes)
            no = HOTSButton(FIF.CLOSE, DARK["red"], T("btn_cancel"))
            no.fit_to_content(min_width=90)
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
            ok.fit_to_content(min_width=90)
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
        self_ref = weakref.ref(self)

        def _do_finish_click(_ref=self_ref, _cb=cb):
            obj = _ref()
            if obj is not None:
                obj._finish_click(_cb)

        _QTimer.singleShot(0, _do_finish_click)

    def _finish_click(self, cb):
        if is_shutting_down() or not shiboken6.isValid(self):

            return
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
        if is_shutting_down() or not shiboken6.isValid(self):
            return False
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
                    self_ref = weakref.ref(self)

                    def _do_close_outside_click(_ref=self_ref):
                        obj = _ref()
                        if obj is not None:
                            obj._close_outside_click()

                    _QTimer.singleShot(0, _do_close_outside_click)
            except Exception:
                pass
        return False

    def _close_outside_click(self):
        if is_shutting_down() or not shiboken6.isValid(self):
            return
        self.hide()
        self.deleteLater()

    def hideEvent(self, event):
        try:
            if shiboken6.isValid(self):
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

class HOTSRadio(QRadioButton):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None, font_pt: float = 10,
                 spacing: int = 12, pad_v: int = 2, accent: Optional[QColor] = None):
        super().__init__(text, parent)
        self._accent = accent
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.TabFocus)
        self.setStyleSheet(
            f"QRadioButton {{ color: {DARK['fg']}; background: transparent; spacing: {spacing}px; "
            f"font-size: {font_pt}pt; padding: {pad_v}px 0px; outline: none; border: none; }}\n"
            "QRadioButton::indicator { width: 16px; height: 16px; background: transparent; border: none; }"
        )
        self._pos = 1.0 if self.isChecked() else 0.0
        self._hover = False
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._on_anim)
        self.toggled.connect(self._on_toggled)

    def _on_anim(self, v):
        self._pos = float(v)
        self.update()

    def _on_toggled(self, checked: bool):
        target = 1.0 if checked else 0.0
        self._anim.stop()
        if not self.isVisible():
            self._pos = target
            self.update()
            return
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(target)
        self._anim.start()

    def enterEvent(self, e):
        self._hover = True
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False
        self.update()
        super().leaveEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        opt = QStyleOptionButton()
        opt.initFrom(self)
        r = self.style().subElementRect(QStyle.SE_RadioButtonIndicator, opt, self)
        d = min(r.width(), r.height())
        cx, cy = r.x() + r.width() / 2, r.y() + r.height() / 2

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.45)

        acc = self._accent or QColor(DARK["accent"])
        off = QColor(0, 0, 0, 64) if IS_LIGHT_THEME else QColor(255, 255, 255, 51)
        t = self._pos
        if self._hover or t > 0:
            line = QColor(acc)
            if t < 1 and not self._hover:
                line = QColor(*(round(off.getRgb()[i] + (acc.getRgb()[i] - off.getRgb()[i]) * t) for i in range(4)))
        else:
            line = off

        p.setPen(QPen(line, 1))
        p.setBrush(Qt.NoBrush)
        rad = (d - 1) / 2
        p.drawEllipse(QRectF(cx - rad, cy - rad, rad * 2, rad * 2))

        if t > 0:
            dot = 4.0 * t
            p.setPen(Qt.NoPen)
            p.setBrush(acc)
            p.drawEllipse(QRectF(cx - dot, cy - dot, dot * 2, dot * 2))


class HOTSSwitch(QCheckBox):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 font_pt: float = 10, color: Optional[str] = None, spacing: int = 12):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.TabFocus)
        self.setStyleSheet(
            f"QCheckBox {{ color: {color or DARK['fg']}; background: transparent; spacing: {spacing}px; "
            f"font-size: {font_pt}pt; padding: 2px 0px; outline: none; border: none; }}\n"
            "QCheckBox::indicator { width: 34px; height: 18px; background: transparent; border: none; }"
        )
        self._pos = 1.0 if self.isChecked() else 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._on_anim)
        self.clicked.connect(self._animate)
        self._hover = False

    def _on_anim(self, v):
        self._pos = float(v)
        self.update()

    def _animate(self, checked: bool):
        self._anim.stop()
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self._anim.stop()
        self._pos = 1.0 if checked else 0.0
        self.update()

    def enterEvent(self, e):
        self._hover = True
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False
        self.update()
        super().leaveEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        opt = QStyleOptionButton()
        opt.initFrom(self)
        r = self.style().subElementRect(QStyle.SE_CheckBoxIndicator, opt, self)
        track = QRectF(r.x() + 0.5, r.y() + 0.5, r.width() - 1, r.height() - 1)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.45)

        t = self._pos
        acc = QColor(DARK["accent"])
        off_fill = QColor(0, 0, 0, 20) if IS_LIGHT_THEME else QColor(255, 255, 255, 30)
        off_line = QColor(0, 0, 0, 64) if IS_LIGHT_THEME else QColor(255, 255, 255, 51)
        off_knob = QColor("#6b6b6b") if IS_LIGHT_THEME else QColor("#bdbdbd")

        def mix(a: QColor, b: QColor) -> QColor:
            return QColor(*(round(a.getRgb()[i] + (b.getRgb()[i] - a.getRgb()[i]) * t) for i in range(4)))

        line = acc if (self._hover and t < 0.5) else mix(off_line, acc)
        p.setPen(QPen(line, 1))
        p.setBrush(mix(off_fill, acc))
        p.drawRoundedRect(track, track.height() / 2, track.height() / 2)

        d = 12
        x0 = track.x() + 3.5
        x1 = track.right() - 3.5 - d
        p.setPen(Qt.NoPen)
        p.setBrush(mix(off_knob, QColor("#ffffff")))
        p.drawEllipse(QRectF(x0 + (x1 - x0) * t, track.y() + (track.height() - d) / 2, d, d))

        if self.hasFocus():
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(acc, 1))
            p.drawRoundedRect(track.adjusted(-2, -2, 2, 2), track.height() / 2 + 2, track.height() / 2 + 2)


class SmoothWheel(QObject):
    """Smooth mouse-wheel scrolling (~150 ms animation instead of a jump). Touchpads,
    high-resolution wheels (pixelDelta) and Ctrl/Shift wheel are left unchanged. For tables it
    works only in ScrollPerPixel mode. step_px: pixels per wheel notch (default: the bar's
    singleStep)."""

    def __init__(self, area: QAbstractScrollArea, step_px: Optional[int] = None):
        super().__init__(area)
        self._area = area
        self._sb = area.verticalScrollBar()
        self._step = step_px
        self._target = None
        self._anim = QPropertyAnimation(self._sb, b"value", self)
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.finished.connect(self._reset)
        self._sb.sliderPressed.connect(self._cancel)
        self._sb.actionTriggered.connect(lambda _a: self._cancel())
        area.viewport().installEventFilter(self)

    def _reset(self):
        self._target = None

    def _cancel(self):
        self._anim.stop()
        self._target = None

    def eventFilter(self, obj, ev):
        if ev.type() != QEvent.Wheel:
            return False
        if ev.modifiers() != Qt.NoModifier or not ev.pixelDelta().isNull():
            return False
        dy = ev.angleDelta().y()
        sb = self._sb
        if dy == 0 or sb.maximum() <= sb.minimum():
            return False
        if isinstance(self._area, QAbstractItemView) and \
                self._area.verticalScrollMode() != QAbstractItemView.ScrollPerPixel:
            return False
        step = self._step or sb.singleStep()
        base = sb.value() if self._target is None else self._target
        target = int(round(base - dy / 120.0 * QApplication.wheelScrollLines() * step))
        target = max(sb.minimum(), min(sb.maximum(), target))
        if target == base:
            # at the edge: let the event propagate (e.g. to the parent) unless an animation is running
            return self._target is not None
        self._target = target
        self._anim.stop()
        self._anim.setStartValue(sb.value())
        self._anim.setEndValue(target)
        self._anim.start()
        ev.accept()
        return True


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

def make_folder_button(path: str, on_click, size: int = 28, icon_size: int = 15,
                        parent: Optional[QWidget] = None):
    btn = TransparentToolButton(FIF.FOLDER, parent)
    btn.setFixedSize(size, size)
    btn.setIconSize(_QSize(icon_size, icon_size))
    btn.setIcon(colored_svg_icon(FIF.FOLDER, QColor(DARK["accent"]), sizes=(icon_size,)))
    btn.setCursor(Qt.PointingHandCursor)
    attach_fluent_tip(btn, path)
    btn.clicked.connect(on_click)
    return btn

class _DWM_MARGINS(ctypes.Structure):
    _fields_ = [("left", ctypes.c_int), ("right", ctypes.c_int),
                ("top",  ctypes.c_int), ("bottom", ctypes.c_int)]

class _DWM_ACCENT_POLICY(ctypes.Structure):
    _fields_ = [("AccentState", ctypes.c_uint), ("AccentFlags", ctypes.c_uint),
                ("GradientColor", ctypes.c_uint), ("AnimationId", ctypes.c_uint)]

class _DWM_WCAD(ctypes.Structure):
    _fields_ = [("Attribute", ctypes.c_int), ("pData", ctypes.c_void_p),
                ("ulDataSize", ctypes.c_ulong)]

_dwm_argtypes_ready = False

def _ensure_dwm_argtypes() -> None:
    global _dwm_argtypes_ready
    if _dwm_argtypes_ready:
        return
    dwmapi = ctypes.windll.dwmapi
    user32 = ctypes.windll.user32

    dwmapi.DwmSetWindowAttribute.argtypes = [
        ctypes.wintypes.HWND, ctypes.wintypes.DWORD,
        ctypes.c_void_p, ctypes.wintypes.DWORD,
    ]
    dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long

    dwmapi.DwmExtendFrameIntoClientArea.argtypes = [
        ctypes.wintypes.HWND, ctypes.POINTER(_DWM_MARGINS),
    ]
    dwmapi.DwmExtendFrameIntoClientArea.restype = ctypes.c_long

    try:
        user32.SetWindowCompositionAttribute.argtypes = [
            ctypes.wintypes.HWND, ctypes.POINTER(_DWM_WCAD),
        ]
        user32.SetWindowCompositionAttribute.restype = ctypes.wintypes.BOOL
    except Exception:
        pass

    _dwm_argtypes_ready = True

def _dwm_dark_titlebar(hwnd: int, dark: bool = True) -> None:
    try:
        import ctypes.wintypes
        _ensure_dwm_argtypes()
        val = ctypes.c_int(1 if dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.wintypes.HWND(hwnd), ctypes.wintypes.DWORD(20),
            ctypes.byref(val), ctypes.wintypes.DWORD(ctypes.sizeof(val)),
        )
    except Exception:
        pass

def _dwm_mica_dialog(hwnd: int, dark: bool = True) -> None:
    try:
        import ctypes.wintypes
        _ensure_dwm_argtypes()
        build = sys.getwindowsversion().build

        if build >= 22000:
            margins = _DWM_MARGINS(-1, -1, -1, -1)
            ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(
                ctypes.wintypes.HWND(hwnd), ctypes.byref(margins)
            )
            if build >= 22621:
                val = ctypes.c_int(2)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.wintypes.HWND(hwnd), ctypes.wintypes.DWORD(38),
                    ctypes.byref(val), ctypes.wintypes.DWORD(ctypes.sizeof(val))
                )
            else:
                val = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.wintypes.HWND(hwnd), ctypes.wintypes.DWORD(1029),
                    ctypes.byref(val), ctypes.wintypes.DWORD(ctypes.sizeof(val))
                )
        else:

            solid_color = 0xFF1A1A2A if dark else 0xFFF2F2F2
            accent = _DWM_ACCENT_POLICY(1, 0, solid_color, 0)
            data   = _DWM_WCAD(19, ctypes.cast(ctypes.byref(accent), ctypes.c_void_p),
                               ctypes.sizeof(accent))
            ctypes.windll.user32.SetWindowCompositionAttribute(
                ctypes.wintypes.HWND(hwnd), ctypes.byref(data)
            )
    except Exception:
        pass

def enable_rounded_corners(hwnd: int):
    try:
        import ctypes.wintypes
        _ensure_dwm_argtypes()
        val = ctypes.c_int(2)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.wintypes.HWND(hwnd), ctypes.wintypes.DWORD(33),
            ctypes.byref(val), ctypes.wintypes.DWORD(ctypes.sizeof(val))
        )
    except Exception:
        pass

class NoScrollbarContextMenuFilter(QObject):

    def eventFilter(self, obj, event):
        if event.type() == QEvent.ContextMenu and isinstance(obj, QScrollBar):
            return True
        return super().eventFilter(obj, event)
