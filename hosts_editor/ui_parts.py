import weakref
from typing import Optional

import shiboken6

from PySide6.QtCore import (
    Qt, QRectF, QSize, QPoint, QEvent, QEasingCurve, QTimer, QAbstractAnimation,
    QPropertyAnimation, QSequentialAnimationGroup, QParallelAnimationGroup,
    Property, Signal,
)
from PySide6.QtGui import QColor, QIcon, QPainter, QPen
from PySide6.QtWidgets import (
    QWidget, QToolButton,
    QFrame, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect,
)

from .constants import DARK, IS_LIGHT_THEME
from .icons import FIF, AppIcon, make_qicon


def theme_color(variant: str = "primary") -> QColor:
    """Accent colour adjusted to the theme. variant: primary, dark1..3, light1..3."""
    h, s, v, _ = QColor(DARK["accent"]).getHsvF()
    if h < 0:
        h = 0.0
    if not IS_LIGHT_THEME:
        s *= 0.84
        v = 1.0
        if variant == "dark1":
            v *= 0.9
        elif variant == "dark2":
            s *= 0.977
            v *= 0.82
        elif variant == "dark3":
            s *= 0.95
            v *= 0.7
        elif variant == "light1":
            s *= 0.92
        elif variant == "light2":
            s *= 0.78
        elif variant == "light3":
            s *= 0.65
    else:
        if variant == "dark1":
            v *= 0.75
        elif variant == "dark2":
            s *= 1.05
            v *= 0.5
        elif variant == "dark3":
            s *= 1.1
            v *= 0.4
        elif variant == "light1":
            v *= 1.05
        elif variant == "light2":
            s *= 0.75
            v *= 1.05
        elif variant == "light3":
            s *= 0.65
            v *= 1.05
    return QColor.fromHsvF(h, min(s, 1.0), min(v, 1.0))


# Each widget sets its OWN stylesheet instead of relying on the app's: pages put selector-less
# rules on frames (e.g. "border: 1px solid ...; border-radius: 6px") that all children inherit,
# and an ancestor's sheet beats the app's, so buttons would get borders. A widget's own sheet
# beats the ancestor's.
if IS_LIGHT_THEME:
    _HOVER, _PRESSED = "rgba(0, 0, 0, 9)", "rgba(0, 0, 0, 6)"
else:
    _HOVER, _PRESSED = "rgba(255, 255, 255, 9)", "rgba(255, 255, 255, 6)"

TOOLBTN_QSS = f"""
QToolButton#hotsToolBtn {{
    background-color: transparent;
    border: none;
    border-radius: 4px;
    margin: 0;
}}
QToolButton#hotsToolBtn:hover {{ background-color: {_HOVER}; }}
QToolButton#hotsToolBtn:pressed {{ background-color: {_PRESSED}; }}
QToolButton#hotsToolBtn:disabled {{ background-color: transparent; }}
"""


class IconWidget(QWidget):
    def __init__(self, icon=None, parent: Optional[QWidget] = None):
        if isinstance(icon, QWidget) and parent is None:  # IconWidget(parent)
            parent, icon = icon, None
        super().__init__(parent)
        self._icon = icon

    def setIcon(self, icon):
        self._icon = icon
        self.update()

    def icon(self):
        return self._icon

    def sizeHint(self) -> QSize:
        return QSize(16, 16)

    def paintEvent(self, _event):
        icon = self._icon
        if icon is None:
            return
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        if isinstance(icon, AppIcon):
            icon.paint(p, QRectF(self.rect()), DARK["fg"])
        elif isinstance(icon, QIcon):
            icon.paint(p, self.rect())


class TransparentToolButton(QToolButton):
    def __init__(self, icon=None, parent: Optional[QWidget] = None):
        if isinstance(icon, QWidget) and parent is None:  # TransparentToolButton(parent)
            parent, icon = icon, None
        super().__init__(parent)
        self.setObjectName("hotsToolBtn")
        self.setStyleSheet(TOOLBTN_QSS)
        self.setCursor(Qt.PointingHandCursor)
        if icon is not None:
            self.setIcon(icon)

    def setIcon(self, icon):
        if isinstance(icon, AppIcon):
            size = self.iconSize().width() or 16
            icon = make_qicon(icon, DARK["fg"], (size,))
        super().setIcon(icon)


class IndeterminateProgressRing(QWidget):
    """Indeterminate progress ring (spinning arc). The animation runs only while the widget
    is visible (start on show, stop on hide), so a hidden ring uses no CPU."""

    def __init__(self, parent: Optional[QWidget] = None, start: bool = True):
        super().__init__(parent)
        self._stroke = 6
        self._start_angle = -180
        self._span_angle = 0
        # _running means "spin while visible" (start=True); the animation actually starts in showEvent.
        self._running = start

        self._start_ani1 = QPropertyAnimation(self, b"startAngle", self)
        self._start_ani1.setDuration(1000)
        self._start_ani1.setStartValue(0)
        self._start_ani1.setEndValue(450)
        self._start_ani2 = QPropertyAnimation(self, b"startAngle", self)
        self._start_ani2.setDuration(1000)
        self._start_ani2.setStartValue(450)
        self._start_ani2.setEndValue(1080)
        start_group = QSequentialAnimationGroup(self)
        start_group.addAnimation(self._start_ani1)
        start_group.addAnimation(self._start_ani2)

        self._span_ani1 = QPropertyAnimation(self, b"spanAngle", self)
        self._span_ani1.setDuration(1000)
        self._span_ani1.setStartValue(0)
        self._span_ani1.setEndValue(180)
        self._span_ani2 = QPropertyAnimation(self, b"spanAngle", self)
        self._span_ani2.setDuration(1000)
        self._span_ani2.setStartValue(180)
        self._span_ani2.setEndValue(0)
        span_group = QSequentialAnimationGroup(self)
        span_group.addAnimation(self._span_ani1)
        span_group.addAnimation(self._span_ani2)

        self._group = QParallelAnimationGroup(self)
        self._group.addAnimation(start_group)
        self._group.addAnimation(span_group)
        self._group.setLoopCount(-1)

        self.setFixedSize(80, 80)

    def _get_start_angle(self) -> int:
        return self._start_angle

    def _set_start_angle(self, angle: int):
        self._start_angle = angle
        self.update()

    def _get_span_angle(self) -> int:
        return self._span_angle

    def _set_span_angle(self, angle: int):
        self._span_angle = angle
        self.update()

    startAngle = Property(int, _get_start_angle, _set_start_angle)
    spanAngle = Property(int, _get_span_angle, _set_span_angle)

    def setStrokeWidth(self, w: int):
        self._stroke = w
        self.update()

    def strokeWidth(self) -> int:
        return self._stroke

    def start(self):
        self._running = True
        if self.isVisible():
            self._begin()

    def stop(self):
        self._running = False
        self._end()

    def _begin(self):
        self._start_angle = 0
        self._span_angle = 0
        self._group.start()

    def _end(self):
        self._group.stop()
        self._start_angle = 0
        self._span_angle = 0

    def showEvent(self, e):
        super().showEvent(e)
        if self._running:
            self._begin()

    def hideEvent(self, e):
        super().hideEvent(e)
        self._group.stop()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing)
        cw = self._stroke
        w = min(self.height(), self.width()) - cw
        rc = QRectF(cw / 2, self.height() / 2 - w / 2, w, w)
        pen = QPen(theme_color("primary"), cw, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        start = -self._start_angle + 180
        p.drawArc(rc, (start % 360) * 16, -self._span_angle * 16)


# kind -> (dark bg, light bg, icon, dark icon colour, light icon colour); "info" uses the theme colour
_BANNER_KINDS = {
    "info":    ((39, 39, 39),  (244, 244, 244), "INFO_FILLED",    None,        None),
    "success": ((57, 61, 27),  (223, 246, 221), "SUCCESS_FILLED", "#6CCB5F",   "#0F7B0F"),
    "warning": ((67, 53, 25),  (255, 244, 206), "WARNING_FILLED", "#FCE100",   "#9D5D00"),
    "error":   ((68, 39, 38),  (253, 231, 233), "ERROR_FILLED",   "#FF99A4",   "#C42B1C"),
}


def _wrap_text(text: str, chars: float) -> str:
    import textwrap
    lines = []
    for para in str(text).split("\n"):
        lines.extend(textwrap.wrap(para, width=int(chars), break_long_words=False) or [""])
    return "\n".join(lines)


class _BannerIcon(QWidget):
    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self._kind = kind

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        _dark_bg, _light_bg, icon_name, dark_c, light_c = _BANNER_KINDS[self._kind]
        color = theme_color("primary") if dark_c is None else QColor(light_c if IS_LIGHT_THEME else dark_c)
        getattr(FIF, icon_name).paint(p, QRectF(10, 10, 15, 15), color)


class InfoBanner(QFrame):
    """Info bar at the top edge of the window: icon, title, content, close button. Kinds: info,
    success, warning, error; horizontal (title beside content) or vertical layout. Banners in
    one window stack; closing one slides the others into its place."""

    closedSignal = Signal()

    MARGIN_TOP = 24
    SPACING = 16
    SLIDE_PX = 16
    _stacks = weakref.WeakKeyDictionary()      # parent -> [banners in the order added]

    def __init__(self, kind: str = "info", title: str = "", content: str = "", parent: QWidget = None,
                 orient=Qt.Horizontal, closable: bool = True, duration: int = -1):
        super().__init__(parent)
        self.setObjectName("hotsInfoBanner")
        self._kind = kind if kind in _BANNER_KINDS else "info"
        self._title_text = title
        self._content_text = content
        self._orient = orient
        self._duration = duration
        self._shown_once = False
        self._closing = False

        light = IS_LIGHT_THEME
        dark_bg, light_bg, _icon, _dc, _lc = _BANNER_KINDS[self._kind]
        r, g, b = light_bg if light else dark_bg
        fg = "black" if light else "white"
        border = "rgb(229, 229, 229)" if light else "rgb(29, 29, 29)"
        self.setStyleSheet(
            f"QFrame#hotsInfoBanner {{ border: 1px solid {border}; border-radius: 6px;"
            f" background-color: rgb({r}, {g}, {b}); }}"
            f"QLabel {{ background-color: transparent; border: none; color: {fg}; font-size: 14px; }}"
        )

        self._icon = _BannerIcon(self._kind, self)
        self._title = QLabel(title, self)
        self._title.setStyleSheet("font-weight: bold;")
        self._title.setVisible(bool(title))
        self._content = QLabel(content, self)
        self._content.setVisible(bool(content))

        self._close_btn = TransparentToolButton(self)
        self._close_btn.setFixedSize(36, 36)
        self._close_btn.setIconSize(QSize(12, 12))
        self._close_btn.setIcon(make_qicon(FIF.CLOSE, "#000000" if IS_LIGHT_THEME else "#ffffff", (12,)))
        self._close_btn.setVisible(closable)
        self._close_btn.clicked.connect(self.close)

        horizontal = (orient == Qt.Horizontal)
        text_lay = QHBoxLayout() if horizontal else QVBoxLayout()
        text_lay.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        text_lay.setAlignment(Qt.AlignTop)
        text_lay.setContentsMargins(1, 8, 0, 8)
        text_lay.setSpacing(5)
        text_lay.addWidget(self._title, 1, Qt.AlignTop)
        if horizontal:
            text_lay.addSpacing(7)
        text_lay.addWidget(self._content, 1, Qt.AlignTop)

        # Slot for extra widgets (see addWidget): a separate column beside the text when
        # horizontal, under the text in the same column when vertical.
        self._widget_lay = QHBoxLayout()
        self._widget_lay.setSpacing(10)
        if horizontal:
            pass
        else:
            text_lay.addLayout(self._widget_lay)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        lay.setSpacing(0)
        lay.addWidget(self._icon, 0, Qt.AlignTop | Qt.AlignLeft)
        lay.addLayout(text_lay)
        if horizontal:
            lay.addLayout(self._widget_lay)
        lay.addSpacing(12)
        lay.addWidget(self._close_btn, 0, Qt.AlignTop | Qt.AlignLeft)

        self._effect = None
        self._slide = None
        self._fade = None
        self._adjust_text()
        parent.installEventFilter(self)

    def addWidget(self, widget: QWidget, stretch: int = 0):
        self._widget_lay.addSpacing(6)
        align = Qt.AlignTop if self._orient == Qt.Vertical else Qt.AlignVCenter
        self._widget_lay.addWidget(widget, stretch, Qt.AlignLeft | align)
        self._adjust_text()

    @classmethod
    def _make(cls, kind, title, content, parent, orient, closable, duration):
        bar = cls(kind, title, content, parent, orient, closable, duration)
        bar.show()
        return bar

    @classmethod
    def info(cls, title: str, content: str, parent: QWidget, orient=Qt.Horizontal,
             closable: bool = True, duration: int = -1) -> "InfoBanner":
        return cls._make("info", title, content, parent, orient, closable, duration)

    @classmethod
    def success(cls, title: str, content: str, parent: QWidget, orient=Qt.Horizontal,
                closable: bool = True, duration: int = -1) -> "InfoBanner":
        return cls._make("success", title, content, parent, orient, closable, duration)

    @classmethod
    def warning(cls, title: str, content: str, parent: QWidget, orient=Qt.Horizontal,
                closable: bool = True, duration: int = -1) -> "InfoBanner":
        return cls._make("warning", title, content, parent, orient, closable, duration)

    @classmethod
    def error(cls, title: str, content: str, parent: QWidget, orient=Qt.Horizontal,
              closable: bool = True, duration: int = -1) -> "InfoBanner":
        return cls._make("error", title, content, parent, orient, closable, duration)

    def _adjust_text(self):
        parent = self.parentWidget()
        w = 900 if parent is None else max(parent.width() - 50, 100)
        self._title.setText(_wrap_text(self._title_text, max(min(w / 10, 120), 30)))
        self._content.setText(_wrap_text(self._content_text, max(min(w / 9, 120), 30)))
        self.adjustSize()

    def _stack(self) -> list:
        return InfoBanner._stacks.setdefault(self.parentWidget(), [])

    def _target_pos(self) -> QPoint:
        p = self.parentWidget()
        stack = self._stack()
        y = self.MARGIN_TOP
        for bar in stack[:stack.index(self)] if self in stack else stack:
            y += bar.height() + self.SPACING
        return QPoint((p.width() - self.width()) // 2, y)

    def showEvent(self, e):
        super().showEvent(e)
        if self._shown_once:
            return
        self._shown_once = True
        self._adjust_text()
        self.raise_()
        self._stack().append(self)
        end = self._target_pos()
        self.move(end.x(), end.y() - self.SLIDE_PX)

        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.0)
        self.setGraphicsEffect(self._effect)

        self._slide = QPropertyAnimation(self, b"pos", self)
        self._slide.setDuration(200)
        self._slide.setEasingCurve(QEasingCurve.OutQuad)
        self._slide.setStartValue(self.pos())
        self._slide.setEndValue(end)

        self._fade = QPropertyAnimation(self._effect, b"opacity", self)
        self._fade.setDuration(200)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.finished.connect(self._drop_effect)

        self._slide.start()
        self._fade.start()

        if self._duration >= 0:
            QTimer.singleShot(self._duration, self._fade_out)

    def _drop_effect(self):
        if not self._closing:
            self.setGraphicsEffect(None)
            self._effect = None

    def _fade_out(self):
        if self._closing or not shiboken6.isValid(self):
            return
        try:
            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(1.0)
            self.setGraphicsEffect(effect)
            self._effect = effect
            ani = QPropertyAnimation(effect, b"opacity", self)
            ani.setDuration(200)
            ani.setStartValue(1.0)
            ani.setEndValue(0.0)
            ani.finished.connect(self.close)
            ani.start()
            self._fade = ani
        except RuntimeError:
            pass

    def eventFilter(self, obj, e):
        if obj is self.parentWidget() and e.type() in (QEvent.Resize, QEvent.WindowStateChange):
            self._adjust_text()
            if self in self._stack() and (self._slide is None or self._slide.state() != QAbstractAnimation.Running):
                self.move(self._target_pos())
        return super().eventFilter(obj, e)

    def closeEvent(self, e):
        if self._closing:
            e.ignore()
            return
        self._closing = True
        stack = self._stack()
        if self in stack:
            stack.remove(self)
        self.closedSignal.emit()
        for bar in list(stack):
            if shiboken6.isValid(bar):
                ani = QPropertyAnimation(bar, b"pos", bar)
                ani.setDuration(200)
                ani.setStartValue(bar.pos())
                ani.setEndValue(bar._target_pos())
                ani.start(QAbstractAnimation.DeleteWhenStopped)
        self.deleteLater()
        e.ignore()
