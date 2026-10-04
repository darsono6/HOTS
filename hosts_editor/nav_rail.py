"""Fixed navigation rail: square icon tiles without labels (names appear only as
tooltips via attach_fluent_tip, to the right of the rail).

The module knows nothing about the window or pages: the caller supplies icons, texts and
callbacks and decides which tile is selected (set_current)."""
import re
from typing import Callable, Dict, Optional

from PySide6.QtCore import Qt, QPointF, QRectF, QSize, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QAbstractButton, QWidget, QVBoxLayout

from .constants import DARK
from .widgets_qt import colored_svg_icon, attach_fluent_tip

_RGBA_RE = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)")


def _css_color(value: str) -> QColor:
    """QColor does not understand 'rgba(r, g, b, a)' from the DARK palette (alpha 0..1)."""
    m = _RGBA_RE.match(value.strip())
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        c = QColor(r, g, b)
        c.setAlphaF(max(0.0, min(1.0, a)))
        return c
    return QColor(value)


def _with_alpha(color: str, alpha: float) -> QColor:
    c = QColor(color)
    c.setAlphaF(alpha)
    return c


class NavTile(QAbstractButton):
    """46x46 icon tile; the widget spans the full rail width (bigger click target), the square is drawn centred."""

    SQUARE = 46
    ICON = 22
    RADIUS = 10
    ROW_H = 50

    def __init__(self, key: str, fif_icon, tooltip: str, rail_width: int, parent=None):
        super().__init__(parent)
        self.key = key
        self._selected = False
        self._hover = False
        self._attention = False
        self._rail_width = rail_width
        self._opacity = 1.0
        self._hover_t = 0.0
        self._sel_t = 0.0

        self.setFixedSize(rail_width, self.ROW_H)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.TabFocus)
        self.setAccessibleName(tooltip)
        self.default_tip = tooltip

        self._opacity_anim = QVariantAnimation(self)
        self._opacity_anim.setDuration(160)
        self._opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._opacity_anim.valueChanged.connect(self._set_opacity)

        self._hover_anim = self._make_anim("_hover_t")
        self._sel_anim = self._make_anim("_sel_t")

        sizes = (self.ICON,)
        self._ico_normal = colored_svg_icon(fif_icon, DARK["fg2"], sizes=sizes)
        self._ico_hover = colored_svg_icon(fif_icon, DARK["fg"], sizes=sizes)
        self._ico_selected = colored_svg_icon(fif_icon, DARK["accent"], sizes=sizes)

        attach_fluent_tip(self, tooltip, side="right", delay_ms=350)

    def _make_anim(self, attr: str) -> QVariantAnimation:
        anim = QVariantAnimation(self)
        anim.setDuration(160)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.valueChanged.connect(lambda v, a=attr: (setattr(self, a, float(v)), self.update()))
        return anim

    def _fade_to(self, anim: QVariantAnimation, attr: str, target: float):
        anim.stop()
        if not self.isVisible():
            setattr(self, attr, target)
            self.update()
            return
        anim.setStartValue(getattr(self, attr))
        anim.setEndValue(target)
        anim.start()

    def _set_opacity(self, value):
        self._opacity = float(value)
        self.update()

    def setEnabled(self, enabled: bool):
        if not enabled and self.hasFocus():
            # Qt moves keyboard focus to the next tile (Tab order) when the focused tile is disabled,
            # which looks like the focus ring jumping to a neighbour. Drop focus ourselves instead.
            self.clearFocus()
        was_enabled = self.isEnabled()
        super().setEnabled(enabled)
        if enabled == was_enabled:
            return
        self._fade_to(self._hover_anim, "_hover_t", 1.0 if (enabled and self._hover) else 0.0)
        self._opacity_anim.stop()
        self._opacity_anim.setStartValue(self._opacity)
        self._opacity_anim.setEndValue(1.0 if enabled else 0.4)
        self._opacity_anim.start()

    def set_tip(self, text: str):
        attach_fluent_tip(self, text, side="right", delay_ms=350)

    def set_selected(self, selected: bool):
        if self._selected != selected:
            self._selected = selected
            self._fade_to(self._sel_anim, "_sel_t", 1.0 if selected else 0.0)

    def set_attention(self, on: bool):
        if self._attention != on:
            self._attention = on
            self.update()

    def sizeHint(self) -> QSize:
        return QSize(self._rail_width, self.ROW_H)

    def enterEvent(self, event):
        self._hover = True
        self._fade_to(self._hover_anim, "_hover_t", 1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self._fade_to(self._hover_anim, "_hover_t", 0.0)
        super().leaveEvent(event)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        sq = self.SQUARE
        x = (self.width() - sq) / 2.0
        y = (self.height() - sq) / 2.0
        box = QRectF(x + 0.5, y + 0.5, sq - 1, sq - 1)

        enabled = self.isEnabled()
        base = self._opacity
        sel = self._sel_t
        pressed = enabled and self.isDown()
        # hover fades out as selection fades in; a press is immediate
        hov = 1.0 if pressed else (self._hover_t if enabled else 0.0)
        hov *= (1.0 - sel)

        if hov > 0:
            bg = _css_color(DARK["panel_bg_strong"] if pressed else DARK["panel_bg_alt"])
            border = _css_color(DARK["border_soft2"])
            bg.setAlphaF(bg.alphaF() * hov)
            border.setAlphaF(border.alphaF() * hov)
            p.setOpacity(base)
            p.setBrush(bg)
            p.setPen(QPen(border, 1))
            p.drawRoundedRect(box, self.RADIUS, self.RADIUS)

        if sel > 0:
            p.setOpacity(base)
            p.setBrush(_with_alpha(DARK["accent"], 0.14 * sel))
            p.setPen(QPen(_with_alpha(DARK["accent"], 0.45 * sel), 1))
            p.drawRoundedRect(box, self.RADIUS, self.RADIUS)

        p.setOpacity(base)
        if enabled and self.hasFocus() and not self._selected:
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(_with_alpha(DARK["accent"], 0.7), 1))
            p.drawRoundedRect(box, self.RADIUS, self.RADIUS)

        if self._attention:
            # Attention outline: same width as the focus outline but more opaque, so it stays
            # visible when the tile is also selected, focused or hovered.
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(_with_alpha(DARK["accent"], 0.9), 1))
            p.drawRoundedRect(box, self.RADIUS, self.RADIUS)

        ix = int(round(x + (sq - self.ICON) / 2.0))
        iy = int(round(y + (sq - self.ICON) / 2.0))
        p.setOpacity(base)
        self._ico_normal.paint(p, ix, iy, self.ICON, self.ICON)
        if hov > 0:
            p.setOpacity(base * hov)
            self._ico_hover.paint(p, ix, iy, self.ICON, self.ICON)
        if sel > 0:
            p.setOpacity(base * sel)
            self._ico_selected.paint(p, ix, iy, self.ICON, self.ICON)

        if sel > 0:
            # Active-page marker at the rail's left edge; rounded only on the right (the left
            # half falls outside the widget and is clipped).
            p.setOpacity(base * sel)
            p.setPen(Qt.NoPen)
            p.setBrush(_css_color(DARK["accent"]))
            bar_h = 22
            p.drawRoundedRect(QRectF(-3, (self.height() - bar_h) / 2.0, 6, bar_h), 3, 3)


class _RailLogo(QWidget):
    def __init__(self, path: str, size: int, parent=None):
        super().__init__(parent)
        self._src = QPixmap(path)
        self._size = size
        self._cache = None      # (dpr, scaled pixmap)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def is_valid(self) -> bool:
        return not self._src.isNull()

    def paintEvent(self, _event):
        if self._src.isNull():
            return
        dpr = self.devicePixelRatioF() or 1.0
        if self._cache is None or self._cache[0] != dpr:
            px = max(1, round(self._size * dpr))
            pm = self._src.scaled(px, px, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pm.setDevicePixelRatio(dpr)
            self._cache = (dpr, pm)
        pm = self._cache[1]
        x = (self._size - pm.width() / dpr) / 2.0
        y = (self._size - pm.height() / dpr) / 2.0
        QPainter(self).drawPixmap(QPointF(x, y), pm)


class NavRail(QWidget):
    WIDTH = 64
    LOGO_MARGIN = 8
    # Logo -> first tile gap, chosen so the first ("home") tile's icon centre lines up with the
    # icon centres in the main toolbar (_build_toolbar in app.py): 48 (title bar) + 20 (view top
    # margin) + 2 (accent line) + 34 (half of the 68 px toolbar) = 104 px from the window top.
    # The rail starts at y=0: 104 - 8 (rail top margin) - 48 (logo) - 25 (half a tile) = 23.
    # Recompute if any of these heights change.
    LOGO_GAP = 23

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navRail")
        self.setFixedWidth(self.WIDTH)

        self._tiles: Dict[str, NavTile] = {}
        self._current: Optional[str] = None

        root = QVBoxLayout(self)
        self._root = root
        root.setContentsMargins(0, 8, 0, 8)
        root.setSpacing(0)
        self._top = QVBoxLayout()
        self._top.setContentsMargins(0, 0, 0, 0)
        self._top.setSpacing(2)
        self._bottom = QVBoxLayout()
        self._bottom.setContentsMargins(0, 0, 0, 0)
        self._bottom.setSpacing(2)
        root.addLayout(self._top)
        root.addStretch(1)
        root.addLayout(self._bottom)

    def set_logo(self, path: str):
        if not path:
            return
        logo = _RailLogo(path, self.WIDTH - 2 * self.LOGO_MARGIN, self)
        if not logo.is_valid():
            logo.deleteLater()
            return
        self._root.insertWidget(0, logo, 0, Qt.AlignHCenter)
        self._root.insertSpacing(1, self.LOGO_GAP)

    def add_tile(self, key: str, fif_icon, tooltip: str,
                 on_click: Callable[[], None], bottom: bool = False) -> NavTile:
        tile = NavTile(key, fif_icon, tooltip, self.WIDTH, self)

        def _handle_click():
            # A click must move keyboard focus to the clicked tile: with Qt.TabFocus alone the mouse
            # does not, so the initially focused "home" tile kept its focus ring after switching pages.
            tile.setFocus(Qt.MouseFocusReason)
            on_click()

        tile.clicked.connect(lambda _checked=False: _handle_click())
        (self._bottom if bottom else self._top).addWidget(tile)
        self._tiles[key] = tile
        return tile

    def tile(self, key: str) -> Optional[NavTile]:
        return self._tiles.get(key)

    def current(self) -> Optional[str]:
        return self._current

    def set_locked(self, locked: bool, tip: str = ""):
        """Disable/enable all tiles; while locked, each tooltip shows the lock reason (`tip`)
        instead of the tile's name."""
        for tile in self._tiles.values():
            tile.setEnabled(not locked)
            tile.set_tip(tip if (locked and tip) else tile.default_tip)

    def set_tile_attention(self, key: str, on: bool):
        tile = self._tiles.get(key)
        if tile is not None:
            tile.set_attention(on)

    def set_current(self, key: Optional[str]):
        self._current = key
        for k, tile in self._tiles.items():
            tile.set_selected(k == key)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.fillRect(self.rect(), _css_color(DARK["panel_bg_strong"]))
        p.setPen(QPen(_css_color(DARK["border_soft"]), 1))
        x = self.width() - 1
        p.drawLine(x, 0, x, self.height())
