import math
import random
import time

from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal, QTimer, QPointF, QRectF, QSize
from PySide6.QtGui import (
    QPainter, QPainterPath, QColor, QLinearGradient, QRadialGradient, QPen,
)

from ..constants import DARK
from ..i18n import T


def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(c1: QColor, c2: QColor, t: float) -> QColor:
    return QColor(
        int(_lerp(c1.red(), c2.red(), t)),
        int(_lerp(c1.green(), c2.green(), t)),
        int(_lerp(c1.blue(), c2.blue(), t)),
    )


class _RetroSupportBannerDark(QWidget):

    clicked = Signal()

    _SKY_TOP = QColor(18, 14, 34)
    _SKY_MID = QColor(78, 40, 66)
    _SKY_LOW = QColor(198, 96, 48)
    _SKY_HORIZON = QColor(255, 176, 112)

    _MOUNTAIN_FAR = QColor(90, 62, 96)
    _MOUNTAIN_MID = QColor(58, 38, 68)
    _MOUNTAIN_NEAR = QColor(26, 18, 36)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(160)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)

        rnd = random.Random(20260713)

        self._frame = 0
        self._hover = False
        self._click_times = []
        self._secret_alpha = 0.0
        self._secret_hold = 0
        self._comet = None
        self._sparkles = []

        self._stars = [
            (rnd.random(), rnd.random() * 0.55, rnd.random() * 6.283, rnd.uniform(0.5, 1.3))
            for _ in range(34)
        ]

        self._mtn_far = self._make_ridge(rnd, base_y=0.50, amp=0.10, n=7, jagged=0.5)
        self._mtn_mid = self._make_ridge(rnd, base_y=0.62, amp=0.13, n=8, jagged=0.8)
        self._mtn_near = self._make_ridge(rnd, base_y=0.80, amp=0.05, n=12, jagged=0.3)

        self._palms = [
            (0.03, 1.05, -6, 0.0),
            (0.075, 0.75, 9, 1.4),
            (0.155, 0.90, -4, 2.6),
            (0.22, 0.65, 7, 0.7),
            (0.80, 0.85, -8, 3.6),
            (0.865, 1.0, 5, 1.9),
            (0.935, 0.70, -5, 4.4),
        ]

        self._clouds = [
            (rnd.random(), rnd.uniform(0.06, 0.24), rnd.uniform(0.7, 1.3), rnd.uniform(0.00006, 0.00014))
            for _ in range(4)
        ]

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(45)

    @staticmethod
    def _make_ridge(rnd, base_y, amp, n, jagged=0.5):
        pts = [(0.0, base_y + rnd.uniform(-amp, amp) * 0.3)]
        for i in range(1, n):
            x = i / n
            peak = (i % 2 == 0)
            depth = amp * (1.0 if peak else jagged)
            y = base_y - depth * rnd.uniform(0.6, 1.0) if peak else base_y + depth * rnd.uniform(0.1, 0.5)
            pts.append((x, y))
        pts.append((1.0, base_y + rnd.uniform(-amp, amp) * 0.3))
        return pts

    def sizeHint(self):
        return QSize(440, 160)

    def showEvent(self, event):
        super().showEvent(event)
        self._timer.start(45)

    def hideEvent(self, event):
        super().hideEvent(event)
        self._timer.stop()

    def _tick(self):
        self._frame += 1

        new_clouds = []
        for (x, y, s, spd) in self._clouds:
            x += spd
            if x > 1.15:
                x = -0.15
            new_clouds.append((x, y, s, spd))
        self._clouds = new_clouds

        alive = []
        for p in self._sparkles:
            p["y"] -= p["speed"]
            p["x"] += p["drift"]
            p["alpha"] = max(0.0, p["alpha"] - 0.02)
            if p["alpha"] > 0.0:
                alive.append(p)
        self._sparkles = alive

        if self._comet is not None:
            c = self._comet
            c["x"] += c["vx"]
            c["y"] += c["vy"]
            c["life"] -= 1
            if c["life"] <= 0 or c["x"] > 1.2 or c["y"] > 1.1:
                self._comet = None

        if self._secret_alpha > 0.0:
            if self._secret_hold > 0:
                self._secret_hold -= 1
            else:
                self._secret_alpha = max(0.0, self._secret_alpha - 0.025)

        self.update()

    def _spawn_sparkles(self, n=10):
        for _ in range(n):
            self._sparkles.append({
                "x": random.uniform(0.1, 0.9),
                "y": random.uniform(0.3, 0.6),
                "speed": random.uniform(0.006, 0.016),
                "drift": random.uniform(-0.002, 0.002),
                "size": random.uniform(1.5, 3.2),
                "alpha": random.uniform(0.6, 1.0),
            })

    def enterEvent(self, event):
        self._hover = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            now = time.time()
            self._click_times = [t for t in self._click_times if now - t < 1.2] + [now]
            self._spawn_sparkles(8)
            if len(self._click_times) >= 5:
                self._click_times = []
                self._secret_alpha = 1.0
                self._secret_hold = 60
                self._comet = {
                    "x": -0.05, "y": random.uniform(0.08, 0.22),
                    "vx": random.uniform(0.012, 0.016),
                    "vy": random.uniform(0.004, 0.008),
                    "life": 90,
                }
            self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            painter.end()
            return

        radius = 10.0
        path = QPainterPath()
        path.moveTo(0, h - radius)
        path.lineTo(0, radius)
        path.quadTo(0, 0, radius, 0)
        path.lineTo(w - radius, 0)
        path.quadTo(w, 0, w, radius)
        path.lineTo(w, h - radius)
        path.quadTo(w, h, w - radius, h)
        path.lineTo(radius, h)
        path.quadTo(0, h, 0, h - radius)
        path.closeSubpath()
        painter.setClipPath(path)

        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, self._SKY_TOP)
        grad.setColorAt(0.45, self._SKY_MID)
        grad.setColorAt(0.8, self._SKY_LOW)
        grad.setColorAt(1.0, self._SKY_HORIZON)
        painter.fillRect(0, 0, w, h, grad)

        def sky_color_at(yf):
            if yf < 0.45:
                return _lerp_color(self._SKY_TOP, self._SKY_MID, yf / 0.45)
            elif yf < 0.8:
                return _lerp_color(self._SKY_MID, self._SKY_LOW, (yf - 0.45) / 0.35)
            return _lerp_color(self._SKY_LOW, self._SKY_HORIZON, min(1.0, (yf - 0.8) / 0.2))

        for (sx, sy, phase, speed) in self._stars:
            tw = (math.sin(self._frame * 0.05 * speed + phase) + 1) / 2
            c = QColor(255, 255, 255)
            c.setAlphaF(0.10 + 0.55 * tw)
            painter.setPen(Qt.NoPen)
            painter.setBrush(c)
            painter.drawEllipse(QPointF(sx * w, sy * h), 1.3, 1.3)

        sun_cx, sun_cy = w * 0.86, h * 0.30
        sun_r = h * 0.30

        for (ring_r_mult, ring_alpha) in [(2.4, 0.05), (1.9, 0.07), (1.45, 0.10)]:
            glow = QColor(self._SKY_HORIZON)
            glow.setAlphaF(ring_alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(QPointF(sun_cx, sun_cy), sun_r * ring_r_mult, sun_r * ring_r_mult)

        sun_grad = QRadialGradient(QPointF(sun_cx, sun_cy), sun_r)
        sun_grad.setColorAt(0.0, QColor(255, 244, 205))
        sun_grad.setColorAt(0.55, QColor(255, 196, 110))
        sun_grad.setColorAt(1.0, QColor(224, 108, 68))
        painter.setBrush(sun_grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(sun_cx, sun_cy), sun_r, sun_r)

        painter.save()
        sun_clip = QPainterPath()
        sun_clip.addEllipse(QPointF(sun_cx, sun_cy), sun_r, sun_r)
        painter.setClipPath(sun_clip, Qt.IntersectClip)
        band_y = sun_cy - sun_r * 0.05
        gap = sun_r * 0.10
        thickness = sun_r * 0.09
        while band_y < sun_cy + sun_r:
            band_col = sky_color_at(band_y / h)
            band_col.setAlphaF(0.9)
            painter.setPen(Qt.NoPen)
            painter.setBrush(band_col)
            painter.drawRect(QRectF(sun_cx - sun_r, band_y, sun_r * 2, thickness))
            band_y += thickness + gap
            gap *= 1.18
            thickness *= 1.05
        painter.restore()

        cloud_puffs = [
            (-14, 2, 7), (-7, -3, 8), (0, -5, 9), (7, -3, 8),
            (14, 2, 7), (-9, 4, 6.5), (0, 5, 8), (9, 4, 6.5),
        ]
        for (cxf, cyf, scale_c, _spd) in self._clouds:
            cx, cy = cxf * w, cyf * h
            dist_to_sun = math.hypot(cx - sun_cx, cy - sun_cy) / max(w, h)
            warmth = max(0.0, 1.0 - dist_to_sun * 1.6) * 0.4
            base = _lerp_color(QColor(70, 62, 92), QColor(150, 108, 90), warmth)
            for (dx, dy, r) in cloud_puffs:
                pr = r * scale_c * (h / 160.0)
                px = cx + dx * scale_c * (h / 160.0)
                py = cy + dy * scale_c * (h / 160.0)
                puff_grad = QRadialGradient(QPointF(px, py), pr)
                c_in = QColor(base)
                c_in.setAlphaF(0.16)
                c_out = QColor(base)
                c_out.setAlphaF(0.0)
                puff_grad.setColorAt(0.0, c_in)
                puff_grad.setColorAt(1.0, c_out)
                painter.setPen(Qt.NoPen)
                painter.setBrush(puff_grad)
                painter.drawEllipse(QPointF(px, py), pr, pr)

        def draw_ridge(pts, color, haze=0.0):
            poly = QPainterPath()
            poly.moveTo(0, h)
            for (xf, yf) in pts:
                poly.lineTo(xf * w, yf * h)
            poly.lineTo(w, h)
            poly.closeSubpath()
            avg_y = sum(yf for (_, yf) in pts) / len(pts)
            c = _lerp_color(QColor(color), sky_color_at(avg_y), haze)
            painter.setPen(Qt.NoPen)
            painter.setBrush(c)
            painter.drawPath(poly)

        draw_ridge(self._mtn_far, self._MOUNTAIN_FAR, haze=0.40)
        draw_ridge(self._mtn_mid, self._MOUNTAIN_MID, haze=0.15)
        draw_ridge(self._mtn_near, self._MOUNTAIN_NEAR, haze=0.0)

        ground_y = self._mtn_near[0][1] * h

        palm_col = QColor(self._MOUNTAIN_NEAR)
        scale_h = h / 160.0
        for (xf, scale_p, tilt_base, phase) in self._palms:
            px = xf * w
            py = ground_y + 3 * scale_h
            trunk_h = 46 * scale_p * scale_h
            trunk_w = 6.0 * scale_p * scale_h
            sway = tilt_base + math.sin(self._frame * 0.02 + phase) * 3.5

            painter.save()
            painter.translate(px, py)
            painter.setPen(Qt.NoPen)
            painter.setBrush(palm_col)

            lean = sway * 0.9
            trunk = QPainterPath()
            trunk.moveTo(-trunk_w / 2, 0)
            trunk.quadTo(lean * 0.35, -trunk_h * 0.5, lean, -trunk_h)
            trunk.lineTo(lean + trunk_w, -trunk_h)
            trunk.quadTo(lean * 0.35 + trunk_w, -trunk_h * 0.5, trunk_w / 2, 0)
            trunk.closeSubpath()
            painter.drawPath(trunk)

            top_x, top_y = lean + trunk_w / 2, -trunk_h
            frond_len = 34 * scale_p * scale_h

            fan_angles = (-70, -42, -18, 4, 26, 50, 76)
            for j, base_angle in enumerate(fan_angles):
                flutter = math.sin(self._frame * 0.06 + phase + j * 1.3) * 5.0
                angle = base_angle + sway * 0.4 + flutter
                painter.save()
                painter.translate(top_x, top_y)
                painter.rotate(angle)
                frond = QPainterPath()
                frond.moveTo(0, 0)
                frond.quadTo(frond_len * 0.22, -frond_len * 0.55, frond_len * 0.08, -frond_len)
                frond.quadTo(frond_len * 0.02, -frond_len * 0.55, -frond_len * 0.12, -frond_len * 0.95)
                frond.closeSubpath()
                painter.setBrush(palm_col)
                painter.drawPath(frond)
                painter.restore()
            painter.restore()

        for p in self._sparkles:
            c = QColor(DARK["accent"])
            c.setAlphaF(max(0.0, min(1.0, p["alpha"])))
            painter.setPen(Qt.NoPen)
            painter.setBrush(c)
            sx, sy, sz = p["x"] * w, p["y"] * h, p["size"]
            painter.drawEllipse(QPointF(sx, sy), sz, sz)

        if self._comet is not None:
            c = self._comet
            cx_, cy_ = c["x"] * w, c["y"] * h
            trail = QPainterPath()
            trail.moveTo(cx_, cy_)
            trail.lineTo(cx_ - c["vx"] * w * 6, cy_ - c["vy"] * h * 6)
            pen = QPen(QColor(255, 240, 200, 160), 2)
            painter.setPen(pen)
            painter.drawPath(trail)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 250, 230))
            painter.drawEllipse(QPointF(cx_, cy_), 3, 3)

        if self._hover:
            glow = QColor(DARK["accent"])
            glow.setAlphaF(0.05)
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow)
            painter.drawRect(QRectF(0, 0, w, h))

        if self._secret_alpha > 0.0:
            painter.save()
            painter.setOpacity(self._secret_alpha)
            msg_font = painter.font()
            msg_font.setPointSize(10)
            msg_font.setBold(True)
            painter.setFont(msg_font)
            painter.setPen(QColor("#ffe6a0"))
            painter.drawText(QRectF(0, 8, w, 22), Qt.AlignHCenter, T("support_comet_msg"))
            painter.restore()

        painter.setClipping(False)
        pen = QPen(QColor(DARK.get("border_soft2", "#444444")))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        painter.end()
