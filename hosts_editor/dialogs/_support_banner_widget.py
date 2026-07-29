import math
import random

from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QPainterPath, QColor, QLinearGradient, QRadialGradient,
    QFont, QPen, QBrush, QPolygonF,
)

from ..constants import DARK
from ..i18n import T


def _hash01(n: float) -> float:
    v = math.sin(n * 12.9898) * 43758.5453
    return v - math.floor(v)


class AnimatedSupportBanner(QWidget):

    def __init__(self, parent=None, height: int = 190):
        super().__init__(parent)
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setCursor(Qt.PointingHandCursor)

        self._t = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)

        rng = random.Random(2024)
        self._palms = [
            (0.02, 1.00, 8, 0.2, 1.05),
            (0.08, 0.86, -6, 1.1, 0.9),
            (0.145, 0.95, 10, 2.0, 1.0),
            (0.60, 0.78, -8, 2.7, 0.85),
            (0.655, 0.90, 6, 0.6, 0.95),
        ]
        self._clouds = [
            (rng.uniform(0.06, 0.22), rng.uniform(6, 14), rng.uniform(0.9, 1.6), rng.random())
            for _ in range(3)
        ]
        self._hearts = [
            (rng.uniform(0.20, 0.55), rng.random(), rng.uniform(7, 11), rng.uniform(0.7, 1.0))
            for _ in range(4)
        ]
        self._lights = [rng.random() for _ in range(14)]

        self._click_count = 0
        self._last_click_t = -99.0
        self._msg_start_t = None

    def stop(self):
        self._timer.stop()

    def start(self):
        if not self._timer.isActive():
            self._timer.start(40)

    def _tick(self):
        self._t += 0.040
        self.update()

    def showEvent(self, event):
        self.start()
        super().showEvent(event)

    def hideEvent(self, event):
        self.stop()
        super().hideEvent(event)

    def mousePressEvent(self, event):
        now = self._t
        if now - self._last_click_t > 2.5:
            self._click_count = 0
        self._click_count += 1
        self._last_click_t = now
        if self._click_count >= 5:
            self._click_count = 0
            self._msg_start_t = now
        super().mousePressEvent(event)


    def paintEvent(self, event):
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return
        t = self._t
        accent = QColor(DARK.get("accent", "#e0a83c"))

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)

        path = QPainterPath()
        radius = 8.0
        path.moveTo(0, h)
        path.lineTo(0, radius)
        path.quadTo(0, 0, radius, 0)
        path.lineTo(w - radius, 0)
        path.quadTo(w, 0, w, radius)
        path.lineTo(w, h)
        path.closeSubpath()
        p.setClipPath(path)

        horizon = h * 0.60

        self._draw_sky(p, w, h, horizon)
        self._draw_sun(p, w, h, horizon, t)
        self._draw_clouds(p, w, h, t)
        self._draw_mountains(p, w, h, horizon)
        self._draw_sea(p, w, h, horizon, t)
        self._draw_diner(p, w, h, horizon, t)

        for fx, hf, lean, phase, scale in self._palms:
            self._draw_palm(p, w, h, horizon, fx, hf, lean, phase, scale, t)

        self._draw_shore(p, w, h)
        self._draw_hearts(p, w, h, horizon, accent, t)
        self._draw_message(p, w, h, t)

        p.end()

    def _draw_sky(self, p, w, h, horizon):
        sky = QLinearGradient(0, 0, 0, horizon)
        sky.setColorAt(0.0, QColor("#2b2d5e"))
        sky.setColorAt(0.35, QColor("#513a6b"))
        sky.setColorAt(0.65, QColor("#a1526f"))
        sky.setColorAt(1.0, QColor("#e8825a"))
        p.fillRect(QRectF(0, 0, w, horizon + 1), sky)

    def _draw_sun(self, p, w, h, horizon, t):
        sun_cx = w * 0.30
        sun_cy = horizon - h * 0.02
        r = h * 0.22
        pulse = 0.9 + 0.1 * math.sin(t * 0.6)
        glow = QRadialGradient(sun_cx, sun_cy, r * 2.4 * pulse)
        glow.setColorAt(0.0, QColor(255, 214, 150, 130))
        glow.setColorAt(0.5, QColor(255, 170, 120, 60))
        glow.setColorAt(1.0, QColor(255, 170, 120, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(QPointF(sun_cx, sun_cy), r * 2.4 * pulse, r * 2.4 * pulse)

        core = QRadialGradient(sun_cx, sun_cy, r)
        core.setColorAt(0.0, QColor(255, 250, 225))
        core.setColorAt(0.6, QColor(255, 214, 140))
        core.setColorAt(1.0, QColor(255, 170, 110))
        p.setBrush(QBrush(core))
        p.drawEllipse(QPointF(sun_cx, sun_cy), r, r)

    def _draw_clouds(self, p, w, h, t):
        p.setPen(Qt.NoPen)
        for ci, (fy, speed, scale, off) in enumerate(self._clouds):
            cw = h * 0.85 * scale
            travel = w + cw
            x = (off * travel + t * speed) % travel - cw
            y = fy * h

            puffs = 2 + (ci % 2)
            for pi in range(puffs):
                seed = ci * 17.3 + pi * 5.1
                pw = cw * (0.55 + 0.45 * _hash01(seed))
                ph_ = h * (0.06 + 0.05 * _hash01(seed + 1))
                px_ = x + cw * (pi / max(1, puffs - 1) if puffs > 1 else 0.5) * 0.7
                py_ = y + (_hash01(seed + 2) - 0.5) * h * 0.05
                grad = QLinearGradient(px_, py_ - ph_ * 0.6, px_, py_ + ph_ * 0.6)
                grad.setColorAt(0.0, QColor(255, 200, 190, 0))
                grad.setColorAt(0.5, QColor(255, 205, 195, 45))
                grad.setColorAt(1.0, QColor(255, 200, 190, 0))
                p.setBrush(QBrush(grad))
                p.drawEllipse(QRectF(px_ - pw / 2, py_ - ph_ / 2, pw, ph_))

    def _draw_mountains(self, p, w, h, horizon):
        pts = [QPointF(0, horizon)]
        n = 7
        ridge = []
        for i in range(n + 1):
            x = w * i / n
            ph = math.sin(i * 1.7 + 0.4) * 0.5 + math.sin(i * 0.6) * 0.3
            y = horizon - h * (0.05 + 0.045 * (ph + 1))
            ridge.append(QPointF(x, y))
            pts.append(QPointF(x, y))
        pts.append(QPointF(w, horizon))
        poly = QPolygonF(pts)

        mgrad = QLinearGradient(0, horizon - h * 0.14, 0, horizon)
        mgrad.setColorAt(0.0, QColor(58, 46, 82, 255))
        mgrad.setColorAt(1.0, QColor(45, 36, 68, 255))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(mgrad))
        p.drawPolygon(poly)

        pen = QPen(QColor(255, 190, 150, 120))
        pen.setWidthF(max(1.0, h * 0.012))
        p.setPen(pen)
        rim = QPainterPath()
        rim.moveTo(ridge[0].x(), ridge[0].y())
        for pt in ridge[1:]:
            rim.lineTo(pt.x(), pt.y())
        p.drawPath(rim)
        p.setPen(Qt.NoPen)

    def _draw_sea(self, p, w, h, horizon, t):
        sea = QLinearGradient(0, horizon, 0, h * 0.90)
        sea.setColorAt(0.0, QColor("#3a2f63"))
        sea.setColorAt(1.0, QColor("#211a3a"))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(sea))
        p.drawRect(QRectF(0, horizon, w, h * 0.90 - horizon))

        sun_cx = w * 0.30
        refl = QLinearGradient(sun_cx, horizon, sun_cx, h * 0.90)
        refl.setColorAt(0.0, QColor(255, 214, 150, 130))
        refl.setColorAt(1.0, QColor(255, 214, 150, 0))
        p.setBrush(QBrush(refl))
        rw = h * 0.40
        p.drawRect(QRectF(sun_cx - rw / 2, horizon, rw, h * 0.90 - horizon))

        p.setPen(Qt.NoPen)
        for i in range(10):
            fx = _hash01(i * 3.1 + 5)
            fy = _hash01(i * 7.7 + 1)
            yy = horizon + fy * (h * 0.90 - horizon)
            shimmer = 0.5 + 0.5 * math.sin(t * 1.4 + i * 2.1)
            if shimmer < 0.55:
                continue
            xx = (fx * w + t * 6) % w
            p.setBrush(QColor(255, 235, 210, int(70 * shimmer)))
            p.drawEllipse(QPointF(xx, yy), 1.6, 1.0)

    def _draw_palm(self, p, w, h, horizon, fx, hf, lean, phase, scale, t):
        base_x = fx * w
        base_y = h * 0.905
        height = h * 0.62 * hf * scale
        sway = math.sin(t * 0.7 + phase) * 3.0

        top_x = base_x + math.sin(math.radians(lean)) * height * 0.35 + sway
        top_y = base_y - height

        trunk = QPainterPath()
        trunk.moveTo(base_x - 3 * scale, base_y)
        trunk.quadTo(base_x + math.sin(math.radians(lean)) * height * 0.15,
                     base_y - height * 0.55,
                     top_x - 2 * scale, top_y + 6 * scale)
        trunk.lineTo(top_x + 2 * scale, top_y + 6 * scale)
        trunk.quadTo(base_x + math.sin(math.radians(lean)) * height * 0.15 + 4 * scale,
                     base_y - height * 0.55,
                     base_x + 3 * scale, base_y)
        trunk.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(15, 12, 20, 235))
        p.drawPath(trunk)

        top = QPointF(top_x, top_y)
        frond_len = height * 0.42
        angles = [-165, -135, -105, -80, -55, -25, 5]
        for i, ang in enumerate(angles):
            wind = math.sin(t * 1.3 + phase + i) * 6
            fpath = self._frond_path(top, ang + wind, frond_len * (0.85 + 0.03 * (i % 3)),
                                      droop=frond_len * 0.55, width=frond_len * 0.10)
            p.drawPath(fpath)

    def _frond_path(self, top: QPointF, angle_deg, length, droop, width):
        ang = math.radians(angle_deg)
        dirx, diry = math.cos(ang), math.sin(ang)
        tip = QPointF(top.x() + dirx * length, top.y() + diry * length + droop)
        perp = QPointF(-diry, dirx)
        base_l = QPointF(top.x() + perp.x() * width * 0.25, top.y() + perp.y() * width * 0.25)
        base_r = QPointF(top.x() - perp.x() * width * 0.25, top.y() - perp.y() * width * 0.25)
        mid = QPointF(top.x() + dirx * length * 0.55, top.y() + diry * length * 0.55 + droop * 0.35)
        ctrl1 = QPointF(mid.x() + perp.x() * width, mid.y() + perp.y() * width)
        ctrl2 = QPointF(mid.x() - perp.x() * width, mid.y() - perp.y() * width)
        path = QPainterPath(base_l)
        path.quadTo(ctrl1, tip)
        path.quadTo(ctrl2, base_r)
        path.closeSubpath()
        return path

    def _draw_diner(self, p, w, h, horizon, t):
        bw = h * 1.26
        bx = w - bw
        roof_y = h * 0.44
        base_y = h * 0.905

        body = QLinearGradient(bx, roof_y, bx, base_y)
        body.setColorAt(0.0, QColor("#4a2f2a"))
        body.setColorAt(1.0, QColor("#241614"))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(body))
        p.drawRect(QRectF(bx, roof_y, bw, base_y - roof_y))

        ridge_h = h * 0.075
        inset = bw * 0.07
        roof = QPainterPath()
        roof.moveTo(bx - h * 0.025, roof_y)
        roof.lineTo(bx + inset, roof_y - ridge_h)
        roof.lineTo(bx + bw - inset, roof_y - ridge_h)
        roof.lineTo(bx + bw + h * 0.025, roof_y)
        roof.closeSubpath()
        roof_grad = QLinearGradient(0, roof_y - ridge_h, 0, roof_y)
        roof_grad.setColorAt(0.0, QColor("#332420"))
        roof_grad.setColorAt(1.0, QColor("#160f0d"))
        p.setBrush(QBrush(roof_grad))
        p.drawPath(roof)

        p.setBrush(QColor("#caa06a"))
        p.drawRect(QRectF(bx - h * 0.025, roof_y - max(1.0, h * 0.012), bw + h * 0.05, max(1.0, h * 0.012)))

        awn_y = roof_y + h * 0.14
        awn_h = h * 0.07
        stripes = 8
        sw = bw / stripes
        for i in range(stripes):
            col = QColor("#c94b4b") if i % 2 == 0 else QColor("#e9e2c9")
            p.setBrush(col)
            p.drawRect(QRectF(bx + i * sw, awn_y, sw + 0.5, awn_h))
        scallop = QPainterPath()
        for i in range(stripes):
            cx = bx + i * sw + sw / 2
            scallop.moveTo(bx + i * sw, awn_y + awn_h)
            scallop.quadTo(cx, awn_y + awn_h + h * 0.025, bx + (i + 1) * sw, awn_y + awn_h)
        scallop.lineTo(bx + bw, awn_y + awn_h)
        scallop.lineTo(bx, awn_y + awn_h)
        scallop.closeSubpath()
        p.setBrush(QColor("#c94b4b"))
        p.drawPath(scallop)

        for i, seed in enumerate(self._lights):
            fx_l = bx + (i + 0.5) / len(self._lights) * bw
            fy_l = awn_y + awn_h + h * 0.02
            tw = 0.5 + 0.5 * math.sin(t * 2.0 + seed * 20)
            if tw < 0.35:
                continue
            p.setBrush(QColor(255, 225, 150, int(230 * tw)))
            p.drawEllipse(QPointF(fx_l, fy_l), 1.6, 1.6)

        win_y = awn_y + awn_h + h * 0.05
        win_h = base_y - win_y - h * 0.03
        n_win = 3
        margin = bw * 0.045
        gap = bw * 0.05
        usable = bw - 2 * margin - gap * (n_win - 1)
        ww = usable / n_win

        p.save()
        p.setClipRect(QRectF(bx, roof_y, bw, base_y - roof_y))
        for i in range(n_win):
            wx = bx + margin + i * (ww + gap)
            glow = QRadialGradient(wx + ww / 2, win_y + win_h / 2, ww * 1.3)
            glow.setColorAt(0.0, QColor(255, 200, 130, 150))
            glow.setColorAt(1.0, QColor(255, 200, 130, 0))
            p.setBrush(QBrush(glow))
            p.drawRect(QRectF(wx - ww * 0.35, win_y - win_h * 0.3, ww * 1.7, win_h * 1.6))
            p.setBrush(QColor(255, 214, 160, 210))
            p.drawRect(QRectF(wx, win_y, ww, win_h))
        p.restore()

        self._draw_neon_sign(p, bx + bw * 0.5, roof_y, bw, h, t)

    def _draw_neon_sign(self, p, cx, roof_y, bw, h, t):
        neon_cycle = 6.0
        nphase = t % neon_cycle
        if nphase > neon_cycle - 0.4:
            ft = nphase - (neon_cycle - 0.4)
            on = int(ft * 26) % 3 != 0
        else:
            on = True
        a_mul = 1.0 if on else 0.22

        board_w = bw * 0.82
        board_h = h * 0.135
        board_x = cx - board_w / 2
        board_y = roof_y - board_h * 0.55

        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#1c1210"))
        post_w = max(2.0, board_w * 0.02)
        p.drawRect(QRectF(board_x + board_w * 0.12, board_y + board_h * 0.6, post_w, board_h * 0.6))
        p.drawRect(QRectF(board_x + board_w * 0.88 - post_w, board_y + board_h * 0.6, post_w, board_h * 0.6))

        board = QLinearGradient(0, board_y, 0, board_y + board_h)
        board.setColorAt(0.0, QColor("#241a2e"))
        board.setColorAt(1.0, QColor("#150f1c"))
        p.setBrush(QBrush(board))
        p.drawRoundedRect(QRectF(board_x, board_y, board_w, board_h), board_h * 0.12, board_h * 0.12)
        p.setPen(QPen(QColor(255, 255, 255, 25), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(board_x, board_y, board_w, board_h), board_h * 0.12, board_h * 0.12)
        p.setPen(Qt.NoPen)

        size = board_h * 0.62
        font = QFont("Arial", int(size))
        font.setBold(True)
        font.setStyleStrategy(QFont.PreferAntialias)
        text = "HOTS"

        tp = QPainterPath()
        tp.addText(0, 0, font, text)
        br = tp.boundingRect()
        tx = cx - br.width() / 2 - br.left()
        ty = board_y + board_h / 2 - br.height() / 2 - br.top()
        tp = QPainterPath()
        tp.addText(tx, ty, font, text)

        grad = QLinearGradient(br.left() + tx, 0, br.right() + tx, 0)
        grad.setColorAt(0.0, QColor(90, 235, 235))
        grad.setColorAt(1.0, QColor(255, 90, 190))

        for width_, alpha in ((7, 25), (4, 45), (2, 90)):
            pen = QPen(QColor(255, 110, 200, int(alpha * a_mul)))
            pen.setWidthF(width_)
            pen.setJoinStyle(Qt.RoundJoin)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            p.drawPath(tp)
        p.setPen(Qt.NoPen)
        if a_mul > 0.5:
            p.setBrush(QBrush(grad))
        else:
            p.setBrush(QColor(120, 70, 90, 160))
        p.drawPath(tp)

        bh = br.height() * 0.85
        for side in (-1, 1):
            bx0 = tx + (br.left() if side < 0 else br.right()) + side * bh * 0.28
            bpath = QPainterPath()
            bpath.moveTo(bx0, ty + br.top() + bh * 0.08)
            bpath.lineTo(bx0 + side * bh * 0.26, ty + br.top() + bh * 0.5)
            bpath.lineTo(bx0, ty + br.top() + bh * 0.92)
            pen = QPen(QColor(255, 110, 200, int(190 * a_mul)))
            pen.setWidthF(2.4)
            pen.setJoinStyle(Qt.RoundJoin)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawPath(bpath)
        p.setPen(Qt.NoPen)

    def _draw_shore(self, p, w, h):
        shore_y = h * 0.905
        shore = QLinearGradient(0, shore_y, 0, h)
        shore.setColorAt(0.0, QColor("#c9a074"))
        shore.setColorAt(1.0, QColor("#8a6a4e"))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(shore))
        p.drawRect(QRectF(0, shore_y, w, h - shore_y))
        p.setBrush(QColor(255, 255, 255, 70))
        p.drawRect(QRectF(0, shore_y - 1.5, w, 3))

    def _draw_hearts(self, p, w, h, horizon, accent, t):
        base_y = h * 0.60
        cycle = h * 0.9
        p.setPen(Qt.NoPen)
        for fx, phase, speed, scale in self._hearts:
            travel = (t * speed + phase * cycle) % cycle
            y = base_y - travel
            fade_in = min(1.0, travel / (h * 0.15))
            fade_out = min(1.0, (cycle - travel) / (h * 0.35))
            alpha = max(0.0, min(fade_in, fade_out)) * 150
            if alpha <= 3:
                continue
            hx = fx * w
            s = 5 * scale
            hp = QPainterPath()
            hp.moveTo(hx, y + s * 0.3)
            hp.cubicTo(hx - s, y - s * 0.6, hx - s * 1.6, y + s * 0.5, hx, y + s * 1.6)
            hp.cubicTo(hx + s * 1.6, y + s * 0.5, hx + s, y - s * 0.6, hx, y + s * 0.3)
            col = QColor(accent.red(), accent.green(), accent.blue(), int(alpha))
            p.setBrush(col)
            p.drawPath(hp)

    def _draw_message(self, p, w, h, t):
        if self._msg_start_t is None:
            return
        dt = t - self._msg_start_t
        fade_in, hold, fade_out = 0.35, 2.6, 1.1
        total = fade_in + hold + fade_out
        if dt > total:
            self._msg_start_t = None
            return
        if dt < fade_in:
            a = dt / fade_in
        elif dt < fade_in + hold:
            a = 1.0
        else:
            a = max(0.0, 1.0 - (dt - fade_in - hold) / fade_out)

        p.setBrush(QColor(18, 13, 26, int(150 * a)))
        p.setPen(Qt.NoPen)
        p.drawRect(QRectF(0, 0, w, h))
        font = QFont("Segoe UI", max(10, int(h * 0.10)))
        font.setBold(True)
        p.setFont(font)
        p.setPen(QColor(255, 244, 214, int(255 * a)))
        p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, T("support_thank_you"))
