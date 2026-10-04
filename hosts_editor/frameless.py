"""Custom frameless main window. On Windows it uses plain ctypes (no pywin32);
on other platforms it is an ordinary frameless Qt window."""
import ctypes
import ctypes.wintypes as wt
import sys
from typing import Optional

from PySide6.QtCore import (
    Qt, QEvent, QPoint, QPointF, QAbstractAnimation, QEasingCurve,
    QPropertyAnimation, QTimer, Signal,
)
from PySide6.QtGui import QColor, QKeySequence, QPainter, QPainterPath, QPen, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QAbstractButton, QAbstractScrollArea, QFrame, QHBoxLayout, QLabel,
    QLayout, QStackedWidget, QWidget,
)

from .constants import IS_LIGHT_THEME

IS_WIN = sys.platform == "win32"


WM_STYLECHANGING = 0x007C
WM_GETMINMAXINFO = 0x0024
WM_SIZE = 0x0005
WM_ENTERSIZEMOVE = 0x0231
WM_EXITSIZEMOVE = 0x0232
SIZE_RESTORED, SIZE_MAXIMIZED = 0, 2
WM_NCCALCSIZE = 0x0083
WM_NCHITTEST = 0x0084
WVR_REDRAW = 0x0300

HTLEFT, HTRIGHT, HTTOP, HTTOPLEFT, HTTOPRIGHT = 10, 11, 12, 13, 14
HTBOTTOM, HTBOTTOMLEFT, HTBOTTOMRIGHT = 15, 16, 17

GWL_STYLE = -16
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_SYSMENU = 0x00080000

WANTED_STYLE = WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_CAPTION | WS_THICKFRAME
# WS_SYSMENU is deliberately left alone: removing it (to hide the system buttons) also
# disabled the shadow and Mica. The system buttons are hidden via DWM margins (see apply_effects).
UNWANTED_STYLE = 0

SWP_NOSIZE, SWP_NOMOVE, SWP_NOZORDER = 0x0001, 0x0002, 0x0004
SWP_NOACTIVATE, SWP_FRAMECHANGED = 0x0010, 0x0020

SM_CXSIZEFRAME, SM_CYSIZEFRAME, SM_CXPADDEDBORDER = 32, 33, 92
MONITOR_DEFAULTTONEAREST = 2
SW_RESTORE = 9
ABM_GETSTATE, ABM_GETTASKBARPOS, ABS_AUTOHIDE = 4, 5, 1

BORDER_WIDTH = 5
AUTOHIDE_STRIP = 2

TITLE_BAR_HEIGHT = 48
CAPTION_BTN_W, CAPTION_BTN_H = 46, 32


class _NCCALCSIZE_PARAMS(ctypes.Structure):
    _fields_ = [("rgrc", wt.RECT * 3), ("lppos", ctypes.c_void_p)]


class _STYLESTRUCT(ctypes.Structure):
    _fields_ = [("styleOld", wt.DWORD), ("styleNew", wt.DWORD)]


class _MINMAXINFO(ctypes.Structure):
    _fields_ = [("ptReserved", wt.POINT), ("ptMaxSize", wt.POINT),
                ("ptMaxPosition", wt.POINT), ("ptMinTrackSize", wt.POINT),
                ("ptMaxTrackSize", wt.POINT)]


class _MARGINS(ctypes.Structure):
    _fields_ = [("cxLeftWidth", ctypes.c_int), ("cxRightWidth", ctypes.c_int),
                ("cyTopHeight", ctypes.c_int), ("cyBottomHeight", ctypes.c_int)]


class _ACCENT_POLICY(ctypes.Structure):
    _fields_ = [("AccentState", ctypes.c_int), ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_uint), ("AnimationId", ctypes.c_int)]


class _WCAD(ctypes.Structure):   # WINDOWCOMPOSITIONATTRIBDATA
    _fields_ = [("Attribute", ctypes.c_int), ("Data", ctypes.c_void_p),
                ("SizeOfData", ctypes.c_size_t)]


class _MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT),
                ("rcWork", wt.RECT), ("dwFlags", wt.DWORD)]


class _APPBARDATA(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("hWnd", wt.HWND), ("uCallbackMessage", wt.UINT),
                ("uEdge", wt.UINT), ("rc", wt.RECT), ("lParam", wt.LPARAM)]


def border_hit_test(x: int, y: int, w: int, h: int, bw: int) -> Optional[int]:
    if bw <= 0:
        return None
    lx, rx, ty, by = x < bw, x > w - bw, y < bw, y > h - bw
    if lx and ty:
        return HTTOPLEFT
    if rx and by:
        return HTBOTTOMRIGHT
    if rx and ty:
        return HTTOPRIGHT
    if lx and by:
        return HTBOTTOMLEFT
    if ty:
        return HTTOP
    if by:
        return HTBOTTOM
    if lx:
        return HTLEFT
    if rx:
        return HTRIGHT
    return None


def enforce_style_bits(style: int) -> int:
    return ((style & 0xFFFFFFFF) | WANTED_STYLE) & ~UNWANTED_STYLE & 0xFFFFFFFF


def maximized_client_rect(work, monitor, autohide_edge: Optional[str]):
    """(left, top, right, bottom) client rect of a maximized window: exactly the monitor
    work area, whatever frame Windows stretched. `work` and `monitor` are (l, t, r, b) tuples.

    1-2 px are trimmed in two cases:
      * auto-hiding taskbar: leave a thin strip at its edge so it can still be revealed;
      * work area == whole monitor (e.g. taskbar on another monitor): Qt would treat the
        window as fullscreen and drop its frame styles, so it would grow instead of maximize."""
    l, t, r, b = work
    if autohide_edge == "left":
        l += AUTOHIDE_STRIP
    elif autohide_edge == "top":
        t += AUTOHIDE_STRIP
    elif autohide_edge == "right":
        r -= AUTOHIDE_STRIP
    elif autohide_edge == "bottom":
        b -= AUTOHIDE_STRIP
    elif tuple(work) == tuple(monitor):
        b -= 1
    return l, t, r, b


def adjust_client_rect(rect, maximized: bool, tx: int, ty: int,
                       autohide_edge: Optional[str]) -> None:
    """Adjust `rect` (an object with left/top/right/bottom) for a window without a system frame.

    A maximized WS_THICKFRAME window is stretched past the work area by the frame thickness;
    undo that. With an auto-hiding taskbar, leave a thin strip at its edge."""
    if not maximized:
        return
    rect.left += tx
    rect.right -= tx
    rect.top += ty
    rect.bottom -= ty
    if autohide_edge == "left":
        rect.left += AUTOHIDE_STRIP
    elif autohide_edge == "top":
        rect.top += AUTOHIDE_STRIP
    elif autohide_edge == "right":
        rect.right -= AUTOHIDE_STRIP
    elif autohide_edge == "bottom":
        rect.bottom -= AUTOHIDE_STRIP


def _to_signed32(v: int) -> int:
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v & 0x80000000 else v


class _Native:
    """Thin user32/shell32 layer using private WinDLL instances, so setting argtypes does not
    affect the rest of the program."""

    def __init__(self):
        u = ctypes.WinDLL("user32")
        self.user32 = u
        u.GetWindowLongW.argtypes = [wt.HWND, ctypes.c_int]
        u.GetWindowLongW.restype = ctypes.c_long
        u.SetWindowLongW.argtypes = [wt.HWND, ctypes.c_int, ctypes.c_long]
        u.SetWindowLongW.restype = ctypes.c_long
        u.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, wt.UINT]
        u.SetWindowPos.restype = wt.BOOL
        u.IsZoomed.argtypes = [wt.HWND]
        u.IsZoomed.restype = wt.BOOL
        u.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
        u.GetWindowRect.restype = wt.BOOL
        u.MonitorFromWindow.argtypes = [wt.HWND, wt.DWORD]
        u.MonitorFromWindow.restype = ctypes.c_void_p
        u.MonitorFromRect.argtypes = [ctypes.POINTER(wt.RECT), wt.DWORD]
        u.MonitorFromRect.restype = ctypes.c_void_p
        u.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(_MONITORINFO)]
        u.GetMonitorInfoW.restype = wt.BOOL
        u.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]
        u.ShowWindow.restype = wt.BOOL
        u.GetSystemMetrics.argtypes = [ctypes.c_int]
        u.GetSystemMetrics.restype = ctypes.c_int
        self._get_dpi = getattr(u, "GetDpiForWindow", None)
        if self._get_dpi is not None:
            self._get_dpi.argtypes = [wt.HWND]
            self._get_dpi.restype = wt.UINT
        self._metrics_dpi = getattr(u, "GetSystemMetricsForDpi", None)
        if self._metrics_dpi is not None:
            self._metrics_dpi.argtypes = [ctypes.c_int, wt.UINT]
            self._metrics_dpi.restype = ctypes.c_int

        self._set_comp_attr = getattr(u, "SetWindowCompositionAttribute", None)
        if self._set_comp_attr is not None:
            self._set_comp_attr.argtypes = [wt.HWND, ctypes.POINTER(_WCAD)]
            self._set_comp_attr.restype = wt.BOOL

        dwm = ctypes.WinDLL("dwmapi")
        dwm.DwmExtendFrameIntoClientArea.argtypes = [wt.HWND, ctypes.POINTER(_MARGINS)]
        dwm.DwmExtendFrameIntoClientArea.restype = ctypes.c_long
        dwm.DwmSetWindowAttribute.argtypes = [wt.HWND, wt.DWORD, ctypes.c_void_p, wt.DWORD]
        dwm.DwmSetWindowAttribute.restype = ctypes.c_long
        self.dwmapi = dwm

        sh = ctypes.WinDLL("shell32")
        sh.SHAppBarMessage.argtypes = [wt.DWORD, ctypes.POINTER(_APPBARDATA)]
        sh.SHAppBarMessage.restype = ctypes.c_size_t
        self.shell32 = sh

    def get_style(self, hwnd: int) -> int:
        return int(self.user32.GetWindowLongW(hwnd, GWL_STYLE)) & 0xFFFFFFFF

    def enforce_style(self, hwnd: int) -> bool:
        style = self.get_style(hwnd)
        new = enforce_style_bits(style)
        if new == style:
            return False
        self.user32.SetWindowLongW(hwnd, GWL_STYLE, _to_signed32(new))
        self.refresh_frame(hwnd)
        return True

    def refresh_frame(self, hwnd: int) -> None:
        """A style/frame change only takes effect after SWP_FRAMECHANGED."""
        self.user32.SetWindowPos(
            hwnd, None, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,
        )

    def show_window(self, hwnd: int, cmd: int) -> None:
        self.user32.ShowWindow(hwnd, cmd)

    def is_maximized(self, hwnd: int) -> bool:
        return bool(self.user32.IsZoomed(hwnd))

    def window_rect(self, hwnd: int):
        r = wt.RECT()
        self.user32.GetWindowRect(hwnd, ctypes.byref(r))
        return r

    def set_size(self, hwnd: int, w: int, h: int) -> None:
        """Set the window size (physical px) without moving it or changing z-order.
        The window has no system frame (WM_NCCALCSIZE), so window size == client size."""
        self.user32.SetWindowPos(hwnd, None, 0, 0, w, h,
                                 SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE)

    def dpi(self, hwnd: int) -> int:
        if self._get_dpi is not None:
            d = int(self._get_dpi(hwnd))
            if d > 0:
                return d
        return 96

    def frame_thickness(self, hwnd: int):
        """(horizontal, vertical) resize-frame thickness in px."""
        dpi = self.dpi(hwnd)

        def metric(idx: int) -> int:
            if self._metrics_dpi is not None:
                return int(self._metrics_dpi(idx, dpi))
            return int(self.user32.GetSystemMetrics(idx))

        pad = metric(SM_CXPADDEDBORDER)
        return metric(SM_CXSIZEFRAME) + pad, metric(SM_CYSIZEFRAME) + pad

    def work_area(self, hwnd: int, rect=None):
        """((l, t, r, b) work area, (l, t, r, b) whole monitor) or None.
        With `rect` (new window rect from WM_NCCALCSIZE) the monitor is chosen by it rather
        than by the current window position, which is correct when moving between monitors."""
        if rect is not None:
            mon = self.user32.MonitorFromRect(ctypes.byref(rect), MONITOR_DEFAULTTONEAREST)
        else:
            mon = self.user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
        mi = _MONITORINFO()
        mi.cbSize = ctypes.sizeof(_MONITORINFO)
        if not mon or not self.user32.GetMonitorInfoW(mon, ctypes.byref(mi)):
            return None
        w, m = mi.rcWork, mi.rcMonitor
        return (w.left, w.top, w.right, w.bottom), (m.left, m.top, m.right, m.bottom)

    def _extend_frame(self, hwnd: int, left: int, right: int, top: int, bottom: int):
        m = _MARGINS(left, right, top, bottom)
        self.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(m))

    def _set_dwm_attr(self, hwnd: int, attr: int, value: int):
        v = ctypes.c_int(value)
        self.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(v), ctypes.sizeof(v))

    def apply_effects(self, hwnd: int, dark: bool, mica: bool, build: int,
                      initial: bool = False) -> None:
        """DWM shadow (margin -1) once at creation; Mica (Win11) after the window is shown.

        With Mica the frame is extended as (16777215, 16777215, 0, 0): left/right maximal,
        top and bottom 0. A -1 top margin hands the whole top area to the system, and DWM
        draws its own caption buttons there (the "doubled" buttons)."""
        if initial or not mica:
            self._extend_frame(hwnd, -1, -1, -1, -1)
        if not mica:
            return
        self._extend_frame(hwnd, 16777215, 16777215, 0, 0)

        if self._set_comp_attr is not None:
            accent = _ACCENT_POLICY(5, 0, 0, 0)               # ACCENT_ENABLE_HOSTBACKDROP
            data = _WCAD(19, ctypes.cast(ctypes.byref(accent), ctypes.c_void_p),
                         ctypes.sizeof(accent))               # WCA_ACCENT_POLICY
            self._set_comp_attr(hwnd, ctypes.byref(data))
            if dark:
                data.Attribute = 26                            # WCA_USEDARKMODECOLORS
                self._set_comp_attr(hwnd, ctypes.byref(data))

        if build < 22523:
            self._set_dwm_attr(hwnd, 1029, 1)                  # Mica (older Win11 builds)
        else:
            self._set_dwm_attr(hwnd, 38, 2)                    # DWMWA_SYSTEMBACKDROP_TYPE = Mica
        self._set_dwm_attr(hwnd, 20, 1 if dark else 0)         # DWMWA_USE_IMMERSIVE_DARK_MODE

    def taskbar_autohide_edge(self, hwnd: int) -> Optional[str]:
        """'left'/'top'/'right'/'bottom' if the taskbar auto-hides and is on the window's
        monitor, else None."""
        abd = _APPBARDATA()
        abd.cbSize = ctypes.sizeof(_APPBARDATA)
        state = self.shell32.SHAppBarMessage(ABM_GETSTATE, ctypes.byref(abd))
        if not (state & ABS_AUTOHIDE):
            return None
        pos = _APPBARDATA()
        pos.cbSize = ctypes.sizeof(_APPBARDATA)
        if not self.shell32.SHAppBarMessage(ABM_GETTASKBARPOS, ctypes.byref(pos)):
            return None

        mon = self.user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
        mi = _MONITORINFO()
        mi.cbSize = ctypes.sizeof(_MONITORINFO)
        if mon and self.user32.GetMonitorInfoW(mon, ctypes.byref(mi)):
            m, t = mi.rcMonitor, pos.rc
            if not (t.left < m.right and t.right > m.left and t.top < m.bottom and t.bottom > m.top):
                return None
        return {0: "left", 1: "top", 2: "right", 3: "bottom"}.get(int(pos.uEdge))


_WIN_BUILD = sys.getwindowsversion().build if IS_WIN else 0   # pylint: disable=no-member

_native: Optional[_Native] = None
if IS_WIN:
    try:
        _native = _Native()
    except Exception as _e:  # pragma: no cover - Windows only
        print(f"Frameless: native init failed: {_e}")


class _PopUpStack(QStackedWidget):
    DELTA_Y = 76
    DURATION_MS = 300

    def __init__(self, parent=None):
        super().__init__(parent)
        self._animated = True
        self._ani: Optional[QPropertyAnimation] = None

    def setAnimationEnabled(self, enabled: bool):
        self._animated = bool(enabled)

    def switch_to(self, widget: QWidget):
        index = self.indexOf(widget)
        if index < 0 or index == self.currentIndex():
            return
        if isinstance(widget, QAbstractScrollArea):
            widget.verticalScrollBar().setValue(0)

        self._finish_animation()
        self.setCurrentIndex(index)
        if not self._animated:
            return

        ani = QPropertyAnimation(widget, b"pos", self)
        ani.setDuration(self.DURATION_MS)
        ani.setEasingCurve(QEasingCurve.OutQuad)
        ani.setStartValue(QPoint(widget.x(), self.DELTA_Y))
        ani.setEndValue(QPoint(widget.x(), 0))
        ani.finished.connect(self._on_ani_finished)
        self._ani = ani
        ani.start()

    def _finish_animation(self):
        ani = self._ani
        if ani is not None and ani.state() == QAbstractAnimation.Running:
            ani.stop()
            ani.finished.disconnect(self._on_ani_finished)
        self._ani = None

    def _on_ani_finished(self):
        self._ani = None


class PageStack(QFrame):
    currentChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("hotsPageStack")
        self.setAttribute(Qt.WA_StyledBackground)
        if IS_LIGHT_THEME:
            border, bg = "rgba(0, 0, 0, 0.068)", "rgba(255, 255, 255, 0.5)"
        else:
            border, bg = "rgba(0, 0, 0, 0.18)", "rgba(255, 255, 255, 0.0314)"
        self.setStyleSheet(
            "QFrame#hotsPageStack {"
            f" border: 1px solid {border}; border-right: none; border-bottom: none;"
            f" border-top-left-radius: 10px; background-color: {bg}; }}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.view = _PopUpStack(self)
        lay.addWidget(self.view)
        self.view.currentChanged.connect(self.currentChanged)

    def setAnimationEnabled(self, enabled: bool):
        self.view.setAnimationEnabled(enabled)

    def addWidget(self, widget: QWidget):
        self.view.addWidget(widget)

    def widget(self, index: int):
        return self.view.widget(index)

    def indexOf(self, widget: QWidget) -> int:
        return self.view.indexOf(widget)

    def count(self) -> int:
        return self.view.count()

    def currentIndex(self) -> int:
        return self.view.currentIndex()

    def currentWidget(self):
        return self.view.currentWidget()

    def setCurrentWidget(self, widget: QWidget):
        self.view.switch_to(widget)

    def setCurrentIndex(self, index: int):
        self.view.switch_to(self.view.widget(index))


class CaptionButton(QAbstractButton):
    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self._maximized = False
        self._hover = False
        self.setFixedSize(CAPTION_BTN_W, CAPTION_BTN_H)
        self.setCursor(Qt.ArrowCursor)
        self.setFocusPolicy(Qt.NoFocus)

    def set_maximized(self, maximized: bool):
        if self._maximized != maximized:
            self._maximized = maximized
            self._hover = False
            self.update()

    def enterEvent(self, e):
        self._hover = True
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False
        self.update()
        super().leaveEvent(e)

    def _colors(self):
        light = IS_LIGHT_THEME
        glyph = QColor(0, 0, 0) if light else QColor(255, 255, 255)
        if self.kind == "close":
            if self.isDown():
                return QColor(255, 255, 255), QColor(241, 112, 122)
            if self._hover:
                return QColor(255, 255, 255), QColor(232, 17, 35)
            return glyph, QColor(0, 0, 0, 0)
        base = 0 if light else 255
        if self.isDown():
            return glyph, QColor(base, base, base, 51)
        if self._hover:
            return glyph, QColor(base, base, base, 26)
        return glyph, QColor(0, 0, 0, 0)

    def paintEvent(self, _event):
        glyph, bg = self._colors()
        p = QPainter(self)
        p.setPen(Qt.NoPen)
        p.setBrush(bg)
        p.drawRect(self.rect())

        # Draw icons in device pixels so 1 px lines stay sharp at any DPI.
        r = self.devicePixelRatioF()
        p.scale(1.0 / r, 1.0 / r)
        pen = QPen(glyph, 1)
        pen.setCosmetic(True)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)

        def px(v: float) -> int:
            return int(round(v * r))

        cx, cy = CAPTION_BTN_W / 2.0, CAPTION_BTN_H / 2.0
        if self.kind == "min":
            p.drawLine(px(cx - 5), px(cy), px(cx + 5), px(cy))
        elif self.kind == "max":
            if not self._maximized:
                p.drawRect(px(cx - 5), px(cy - 5), px(10), px(10))
            else:
                p.drawRect(px(cx - 5), px(cy - 3), px(8), px(8))
                x0, y0, dw = px(cx - 5) + px(2), px(cy - 3), px(2)
                path = QPainterPath(QPointF(x0, y0))
                path.lineTo(x0, y0 - dw)
                path.lineTo(x0 + px(8), y0 - dw)
                path.lineTo(x0 + px(8), y0 - dw + px(8))
                path.lineTo(x0 + px(8) - dw, y0 - dw + px(8))
                p.drawPath(path)
        else:
            # No antialiasing: a 1 px diagonal would blur across two pixels (matches the native X).
            p.setRenderHint(QPainter.Antialiasing, False)
            x0, y0, x1, y1 = px(cx - 5), px(cy - 5), px(cx + 5), px(cy + 5)
            p.drawLine(x0, y0, x1, y1)
            p.drawLine(x1, y0, x0, y1)


class TitleBar(QWidget):
    def __init__(self, window: QWidget):
        super().__init__(window)
        self.setFixedHeight(TITLE_BAR_HEIGHT)

        self.minBtn = CaptionButton("min", self)
        self.maxBtn = CaptionButton("max", self)
        self.closeBtn = CaptionButton("close", self)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(0)
        # No layout-wide setAlignment: buttons are AlignTop individually, while the logo is
        # centred in the full 48 px bar.
        self._logo: Optional[QLabel] = None
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.minBtn, 0, Qt.AlignTop)
        self.hBoxLayout.addWidget(self.maxBtn, 0, Qt.AlignTop)
        self.hBoxLayout.addWidget(self.closeBtn, 0, Qt.AlignTop)

        self.minBtn.clicked.connect(window.showMinimized)
        self.maxBtn.clicked.connect(self._toggle_maximized)
        self.closeBtn.clicked.connect(window.close)
        window.installEventFilter(self)
        self.sync_maximized()

    def sync_maximized(self):
        """Set the glyph from the REAL window state (IsZoomed), not Qt's: Qt is wrong when it
        treats a screen-sized window as fullscreen."""
        w = self.window()
        if hasattr(w, "isMaximizedNative"):
            state = w.isMaximizedNative() or w.isFullscreenMode()
        else:
            state = w.isMaximized()
        self.maxBtn.set_maximized(state)

    def set_logo(self, pixmap: QPixmap, left_margin: int = 10):
        if self._logo is None:
            self._logo = QLabel(self)
            self._logo.setAttribute(Qt.WA_TransparentForMouseEvents)
            self._logo.setStyleSheet("background: transparent;")
            self.hBoxLayout.insertSpacing(0, left_margin)
            self.hBoxLayout.insertWidget(1, self._logo, 0, Qt.AlignVCenter)
        self._logo.setPixmap(pixmap)

    def _toggle_maximized(self):
        w = self.window()
        if hasattr(w, "toggleMaximizeOrFullscreen"):
            w.toggleMaximizeOrFullscreen()
        elif w.isMaximized():
            w.showNormal()
        else:
            w.showMaximized()

    def eventFilter(self, obj, e):
        if obj is self.window() and e.type() == QEvent.WindowStateChange:
            self.sync_maximized()
        return super().eventFilter(obj, e)

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._toggle_maximized()

    def mouseMoveEvent(self, e):
        # Start the drag on mouse move, not on press, so a double-click can still reach the window.
        if not (e.buttons() & Qt.LeftButton):
            return
        if getattr(self.window(), "_fullscreen_mode", False):
            return
        handle = self.window().windowHandle()
        if handle is not None:
            handle.startSystemMove()


class FramelessWindow(QWidget):
    """The app inserts its navigation rail into `hBoxLayout` (index 0) and reports its
    width via setTitleBarOffset()."""

    # False: the maximize button (and title-bar double-click) does a normal maximize to the
    # work area, with the Windows animation. True: fullscreen over the whole monitor, taskbar
    # included (Windows doesn't animate that). F11 always toggles fullscreen.
    MAXIMIZE_MEANS_FULLSCREEN = False

    MIN_WINDOW_SIZE = (0, 0)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._titlebar_offset = 0
        self._fullscreen_mode = False
        self._good_px = None        # last good normal-window size (physical px)
        self._was_max = False
        self._in_sizemove = False
        self._mica = bool(IS_WIN and sys.getwindowsversion().build >= 22000)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        # The app sets the minimum (setMinimumSize); the layout must not raise it
        # (tallest page + title bar gave 662 px instead of 650).
        self.hBoxLayout.setSizeConstraint(QLayout.SetNoConstraint)

        self.stackedWidget = PageStack(self)
        self.widgetLayout = QHBoxLayout()
        self.widgetLayout.setContentsMargins(0, TITLE_BAR_HEIGHT, 0, 0)
        self.widgetLayout.addWidget(self.stackedWidget)
        self.hBoxLayout.addLayout(self.widgetLayout, 1)

        self.titleBar = TitleBar(self)
        self._init_native()
        self._layout_title_bar()
        self.titleBar.raise_()
        self.stackedWidget.currentChanged.connect(lambda _i: self._guard_size_soon())

        QShortcut(QKeySequence(Qt.Key_F11), self, activated=self.toggleFullscreenMode)

    def switchTo(self, page: QWidget):
        self.stackedWidget.setCurrentWidget(page)

    def setTitleBarOffset(self, left: int):
        self._titlebar_offset = max(0, int(left))
        self._layout_title_bar()

    def isFullscreenMode(self) -> bool:
        return self._fullscreen_mode

    def enterFullscreenMode(self):
        if self._fullscreen_mode:
            return
        # Set the flag BEFORE showFullScreen(): it disables style enforcement (otherwise
        # WM_STYLECHANGING restores the frame and the taskbar stays on top).
        self._fullscreen_mode = True
        self.showFullScreen()
        self.titleBar.sync_maximized()

    def exitFullscreenMode(self):
        if not self._fullscreen_mode:
            return
        self._fullscreen_mode = False
        self.showNormal()
        self._reapply_native_soon()
        self.titleBar.sync_maximized()

    def toggleFullscreenMode(self):
        if self._fullscreen_mode:
            self.exitFullscreenMode()
        else:
            self.enterFullscreenMode()

    def toggleMaximizeOrFullscreen(self):
        if self._fullscreen_mode:
            self.exitFullscreenMode()
        elif self.isMaximizedNative():
            self.restoreFromMaximized()
        elif self.MAXIMIZE_MEANS_FULLSCREEN:
            self.enterFullscreenMode()
        else:
            self.showMaximized()

    def restoreFromMaximized(self):
        """Restore a maximized window. Windows' state can disagree with Qt's (showNormal() then
        does nothing), so after a moment check IsZoomed and ask Windows to restore directly."""
        self.showNormal()
        QTimer.singleShot(80, self._force_restore)

    def _force_restore(self):
        try:
            if IS_WIN and _native is not None:
                hwnd = int(self.winId())
                if _native.is_maximized(hwnd):
                    _native.show_window(hwnd, SW_RESTORE)
        except Exception as e:
            print(f"Restore warning: {e}")
        self.titleBar.sync_maximized()

    def _layout_title_bar(self):
        left = self._titlebar_offset
        self.titleBar.setGeometry(left, 0, max(0, self.width() - left), TITLE_BAR_HEIGHT)
        self.titleBar.raise_()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._layout_title_bar()
        self.titleBar.sync_maximized()

    def paintEvent(self, e):
        # With Mica the system (DWM) paints the background; otherwise a solid colour.
        if self._mica:
            return
        bg = QColor(240, 244, 249) if IS_LIGHT_THEME else QColor(32, 32, 32)
        p = QPainter(self)
        p.fillRect(self.rect(), bg)

    def isMaximizedNative(self) -> bool:
        if IS_WIN and _native is not None:
            try:
                return _native.is_maximized(int(self.winId()))
            except Exception:
                pass
        return self.isMaximized()

    def _init_native(self):
        # Windows: a normal window without title-bar background (NoTitleBarBackgroundHint,
        # Qt >= 6.10); the system frame is removed via WM_NCCALCSIZE. With FramelessWindowHint
        # on Qt 6.11, Mica, shadow and animations did not work although the DWM calls succeeded.
        # Where the flag is missing (older Qt) and off Windows, FramelessWindowHint is used.
        hint = getattr(Qt, "NoTitleBarBackgroundHint", None)
        if IS_WIN and hint is not None:
            self.setWindowFlags((self.windowFlags() & ~Qt.FramelessWindowHint) | Qt.Window | hint)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        if not IS_WIN or _native is None:
            return
        try:
            self._apply_native(initial=True)     # creates the HWND (winId)
            handle = self.windowHandle()
            if handle is not None:
                handle.screenChanged.connect(self._on_screen_changed)
        except Exception as e:
            print(f"Frameless init warning: {e}")

    def _apply_native(self, initial: bool = False):
        """Window style + DWM effects. Idempotent, so safe to call repeatedly (constructor, show,
        right after it, activation): Qt can overwrite the style and extended frame after showEvent
        (described since Qt 6.8)."""
        if not IS_WIN or _native is None:
            return
        try:
            hwnd = int(self.winId())
            if not self._fullscreen_mode:
                _native.enforce_style(hwnd)
            _native.apply_effects(hwnd, dark=not IS_LIGHT_THEME, mica=self._mica,
                                  build=_WIN_BUILD, initial=initial)
        except Exception as e:
            print(f"Frameless native warning: {e}")

    def _reapply_native_soon(self):
        QTimer.singleShot(0, self._apply_native)
        QTimer.singleShot(120, self._apply_native)

    def showEvent(self, e):
        super().showEvent(e)
        self._apply_native()
        QTimer.singleShot(0, self._apply_native)
        QTimer.singleShot(250, self._apply_native)
        if self._good_px is None:
            QTimer.singleShot(600, self._remember_good_size)

    def changeEvent(self, e):
        super().changeEvent(e)
        t = e.type()
        if t == QEvent.WindowStateChange:
            # Fullscreen may have been left behind our back (e.g. showNormal() on second-instance
            # activation, Win+Arrow); resync our flag.
            QTimer.singleShot(0, self._sync_fullscreen_flag)
            if IS_WIN and _native is not None and not self._fullscreen_mode:
                try:
                    _native.enforce_style(int(self.winId()))
                except Exception:
                    pass
        elif t == QEvent.ActivationChange and self.isActiveWindow():
            self._apply_native()      # keep Mica/shadow after activation changes

    # Size guard: after maximize/restore (or opening a page) the window can grow by a dozen
    # pixels (Qt adds a system frame the window doesn't have). Remember the size when it is
    # certain (after an edge drag, shortly after show) and restore it natively.
    def _is_normal_native(self, hwnd: int) -> bool:
        return not (self._fullscreen_mode or _native.is_maximized(hwnd) or self.isMinimized())

    def _remember_good_size(self):
        if not IS_WIN or _native is None:
            return
        try:
            hwnd = int(self.winId())
            if self._is_normal_native(hwnd):
                rc = _native.window_rect(hwnd)
                self._good_px = (rc.right - rc.left, rc.bottom - rc.top)
        except Exception:
            pass

    def _guard_size_soon(self, exact: bool = False):
        # exact=True (after restore from maximize): fix any difference; False (page change):
        # only small deviations, so e.g. Win+Arrow isn't undone.
        for ms in (0, 120, 350):
            QTimer.singleShot(ms, lambda e=exact: self._guard_size(e))

    def _guard_size(self, exact: bool):
        if not IS_WIN or _native is None or self._good_px is None or self._in_sizemove:
            return
        try:
            hwnd = int(self.winId())
            if not self._is_normal_native(hwnd):
                return
            rc = _native.window_rect(hwnd)
            w, h = rc.right - rc.left, rc.bottom - rc.top
            gw, gh = self._good_px
            if (w, h) == (gw, gh):
                return
            if not exact and (abs(w - gw) > 40 or abs(h - gh) > 40):
                return
            _native.set_size(hwnd, gw, gh)
        except Exception as e:
            print(f"Size guard warning: {e}")

    def _wanted_min_size(self):
        """Minimum size requested by the app (MIN_WINDOW_SIZE), not what Qt computed from the layout."""
        from PySide6.QtCore import QSize
        w, h = getattr(self, "MIN_WINDOW_SIZE", (0, 0))
        return QSize(w, h) if w and h else self.minimumSize()

    def _sync_fullscreen_flag(self):
        if self._fullscreen_mode and not self.isFullScreen():
            self._fullscreen_mode = False
            self._reapply_native_soon()
        self.titleBar.sync_maximized()

    def _on_screen_changed(self, *_):
        # On monitor/DPI change Windows must recompute the frame (WM_NCCALCSIZE).
        try:
            if _native is not None:
                _native.refresh_frame(int(self.winId()))
        except Exception:
            pass

    def nativeEvent(self, eventType, message):
        if not IS_WIN or _native is None:
            return super().nativeEvent(eventType, message)
        try:
            if not bytes(eventType).startswith(b"windows_"):
                return False, 0
            address = int(message)
            if not address:      # from_address(0) would crash the process instead of raising
                return False, 0
            return self._handle_message(wt.MSG.from_address(address))
        except Exception:
            return False, 0

    def _handle_message(self, msg):
        if not msg.hWnd:
            return False, 0
        hwnd = int(msg.hWnd)

        if msg.message == WM_STYLECHANGING:
            # Qt (or someone else) is changing the window style: fix it in flight so
            # WANTED_STYLE never disappears. No intervention in fullscreen.
            if not self._fullscreen_mode and (msg.wParam & 0xFFFFFFFF) == 0xFFFFFFF0:   # GWL_STYLE (-16)
                ss = ctypes.cast(msg.lParam, ctypes.POINTER(_STYLESTRUCT)).contents
                ss.styleNew = enforce_style_bits(ss.styleNew)
            return False, 0

        if msg.message == WM_ENTERSIZEMOVE:
            self._in_sizemove = True
            return False, 0

        if msg.message == WM_EXITSIZEMOVE:
            self._in_sizemove = False
            QTimer.singleShot(0, self._remember_good_size)
            return False, 0

        if msg.message == WM_SIZE:
            kind = msg.wParam & 0xFFFF
            if kind == SIZE_MAXIMIZED:
                self._was_max = True
            elif kind == SIZE_RESTORED and self._was_max:
                self._was_max = False
                if not self._fullscreen_mode and self._good_px is not None:
                    self._guard_size_soon(exact=True)
            return False, 0

        if msg.message == WM_GETMINMAXINFO:
            # WM_NCCALCSIZE removes the whole non-client area, so window rect == client rect.
            # Qt would add the system frame/caption size to the minimum, making the window
            # snap above minimumSize() once the user drags it.
            if self._fullscreen_mode:
                return False, 0
            mmi = ctypes.cast(msg.lParam, ctypes.POINTER(_MINMAXINFO)).contents
            ms = self._wanted_min_size()
            scale = self.devicePixelRatioF()
            mmi.ptMinTrackSize.x = round(ms.width() * scale)
            mmi.ptMinTrackSize.y = round(ms.height() * scale)
            return True, 0

        if msg.message == WM_NCHITTEST:
            if self._fullscreen_mode or _native.is_maximized(hwnd):
                return False, 0
            x = ctypes.c_short(msg.lParam & 0xFFFF).value
            y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
            rc = _native.window_rect(hwnd)
            bw = max(1, round(BORDER_WIDTH * _native.dpi(hwnd) / 96.0))
            code = border_hit_test(x - rc.left, y - rc.top,
                                   rc.right - rc.left, rc.bottom - rc.top, bw)
            if code is not None:
                return True, code
            return False, 0

        if msg.message == WM_NCCALCSIZE:
            if msg.wParam:
                rect = ctypes.cast(msg.lParam, ctypes.POINTER(_NCCALCSIZE_PARAMS)).contents.rgrc[0]
            else:
                rect = ctypes.cast(msg.lParam, ctypes.POINTER(wt.RECT)).contents
            if _native.is_maximized(hwnd):
                edge = _native.taskbar_autohide_edge(hwnd)
                area = _native.work_area(hwnd, rect)
                if area is not None:
                    rect.left, rect.top, rect.right, rect.bottom = maximized_client_rect(
                        area[0], area[1], edge)
                else:   # fallback: undo the frame stretch
                    tx, ty = _native.frame_thickness(hwnd)
                    adjust_client_rect(rect, True, tx, ty, edge)
            return True, (WVR_REDRAW if msg.wParam else 0)

        return False, 0
