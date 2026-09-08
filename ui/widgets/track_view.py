"""Track Visualization Widget using PySide6 QPainter.

Renders high-fidelity authentic 2D racing circuit geometries with:
- Aspect-ratio preserved fitInView coordinate mapping
- Smooth Catmull-Rom spline interpolation
- Cumulative arc-length distance lookup for car synchronization
- Perpendicular Start/Finish line and physical sector demarcations
- Real-time car markers and telemetry highlights
"""

import bisect
import math
from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.theme import THEME


@dataclass
class CarMarkerData:
    """Position and visual state of a car on the track."""
    driver_name: str
    driver_number: int
    progress: float  # 0.0 to 1.0 along the track
    color_hex: str
    is_selected: bool


class TrackCircuitCanvas(QWidget):
    """QPainter canvas rendering authentic circuit geometry and live telemetry markers."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumSize(320, 240)

        # Default Prototype Circuit waypoints
        default_waypoints = [
            (0.20, 0.82), (0.35, 0.82), (0.50, 0.82), (0.65, 0.82),
            (0.78, 0.80), (0.86, 0.75), (0.88, 0.65), (0.84, 0.54),
            (0.74, 0.46), (0.76, 0.36), (0.82, 0.26), (0.84, 0.18),
            (0.78, 0.14), (0.70, 0.15), (0.58, 0.20), (0.45, 0.22),
            (0.32, 0.22), (0.22, 0.19), (0.16, 0.26), (0.18, 0.35),
            (0.24, 0.42), (0.30, 0.50), (0.28, 0.60), (0.20, 0.68),
            (0.14, 0.72), (0.14, 0.79), (0.16, 0.82),
        ]

        self._raw_waypoints: list[tuple[float, float]] = default_waypoints
        self._track_points: list[tuple[float, float]] = []
        self._tangents: list[tuple[float, float]] = []
        self._cumulative_distances: list[float] = [0.0]
        self._total_spline_length: float = 1.0
        self._sector_fractions: tuple[float, float] = (1700.0 / 5200.0, 3500.0 / 5200.0)

        self._min_x: float = 0.05
        self._max_x: float = 0.95
        self._min_y: float = 0.05
        self._max_y: float = 0.95

        self._track_name: str = "Prototype Circuit"
        self._track_length_m: float = 5200.0

        self._cars: list[CarMarkerData] = []

        self._build_spline(default_waypoints)

    def _build_spline(self, raw_waypoints: list[tuple[float, float]]) -> None:
        """Constructs a smooth Catmull-Rom closed spline and cumulative distance table."""
        if not raw_waypoints or len(raw_waypoints) < 4:
            return

        self._raw_waypoints = raw_waypoints
        self._track_points = []
        self._tangents = []
        self._cumulative_distances = [0.0]

        steps_per_segment = 24
        total_pts = len(raw_waypoints)

        # Generate interpolated spline vertices
        for i in range(total_pts):
            p0 = raw_waypoints[(i - 1) % total_pts]
            p1 = raw_waypoints[i]
            p2 = raw_waypoints[(i + 1) % total_pts]
            p3 = raw_waypoints[(i + 2) % total_pts]

            for s in range(steps_per_segment):
                t = s / steps_per_segment
                t2 = t * t
                t3 = t2 * t

                # Standard Catmull-Rom formulation
                x = 0.5 * (
                    (2.0 * p1[0])
                    + (-p0[0] + p2[0]) * t
                    + (2.0 * p0[0] - 5.0 * p1[0] + 4.0 * p2[0] - p3[0]) * t2
                    + (-p0[0] + 3.0 * p1[0] - 3.0 * p2[0] + p3[0]) * t3
                )
                y = 0.5 * (
                    (2.0 * p1[1])
                    + (-p0[1] + p2[1]) * t
                    + (2.0 * p0[1] - 5.0 * p1[1] + 4.0 * p2[1] - p3[1]) * t2
                    + (-p0[1] + 3.0 * p1[1] - 3.0 * p2[1] + p3[1]) * t3
                )
                self._track_points.append((x, y))

        n_pts = len(self._track_points)
        if n_pts < 2:
            return

        # Calculate cumulative perimeter distance
        cum_dist = 0.0
        for i in range(1, n_pts):
            x0, y0 = self._track_points[i - 1]
            x1, y1 = self._track_points[i]
            cum_dist += math.hypot(x1 - x0, y1 - y0)
            self._cumulative_distances.append(cum_dist)

        # Closing segment distance
        xf, yf = self._track_points[-1]
        x0, y0 = self._track_points[0]
        self._total_spline_length = cum_dist + math.hypot(x0 - xf, y0 - yf)
        if self._total_spline_length < 1e-6:
            self._total_spline_length = 1.0

        # Calculate unit tangents and normals for all spline points
        for i in range(n_pts):
            prev_pt = self._track_points[(i - 1) % n_pts]
            next_pt = self._track_points[(i + 1) % n_pts]
            dx = next_pt[0] - prev_pt[0]
            dy = next_pt[1] - prev_pt[1]
            length = math.hypot(dx, dy)
            if length > 1e-6:
                self._tangents.append((dx / length, dy / length))
            else:
                self._tangents.append((1.0, 0.0))

        # Compute bounding box
        xs = [p[0] for p in self._track_points]
        ys = [p[1] for p in self._track_points]
        self._min_x = min(xs)
        self._max_x = max(xs)
        self._min_y = min(ys)
        self._max_y = max(ys)

    def set_track(self, track: Any) -> None:
        """Dynamically loads track waypoints, metadata, and updates sector boundaries."""
        waypoints = getattr(track, "waypoints", [])
        if waypoints and len(waypoints) >= 4:
            self._build_spline(waypoints)

        if hasattr(track, "sector_lengths") and hasattr(track, "length") and track.length > 0:
            s1, s2, _ = track.sector_lengths
            self._sector_fractions = (s1 / track.length, (s1 + s2) / track.length)
            self._track_name = getattr(track, "name", "Circuit")
            self._track_length_m = getattr(track, "length", 0.0)

        self.update()

    def set_cars(self, cars: list[CarMarkerData]) -> None:
        """Updates car positions along the circuit."""
        self._cars = cars
        self.update()

    def get_point_and_tangent_at_progress(
        self, progress: float
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
        """Calculates normalized position (x, y), unit tangent (tx, ty), and unit normal (nx, ny)."""
        if not self._track_points:
            return ((0.5, 0.5), (1.0, 0.0), (0.0, 1.0))

        norm_prog = (progress % 1.0 + 1.0) % 1.0
        target_dist = norm_prog * self._total_spline_length

        idx = bisect.bisect_right(self._cumulative_distances, target_dist) - 1
        idx = max(0, min(idx, len(self._track_points) - 1))
        next_idx = (idx + 1) % len(self._track_points)

        d0 = self._cumulative_distances[idx]
        d1 = (
            self._cumulative_distances[next_idx]
            if next_idx > idx
            else self._total_spline_length
        )

        segment_len = max(1e-6, d1 - d0)
        frac = max(0.0, min(1.0, (target_dist - d0) / segment_len))

        x0, y0 = self._track_points[idx]
        x1, y1 = self._track_points[next_idx]
        px = x0 + frac * (x1 - x0)
        py = y0 + frac * (y1 - y0)

        t0 = self._tangents[idx]
        t1 = self._tangents[next_idx]
        tx = t0[0] + frac * (t1[0] - t0[0])
        ty = t0[1] + frac * (t1[1] - t0[1])
        t_len = math.hypot(tx, ty)
        if t_len > 1e-6:
            tx /= t_len
            ty /= t_len
        else:
            tx, ty = (1.0, 0.0)

        # Normal vector perpendicular to forward tangent
        nx = -ty
        ny = tx

        return ((px, py), (tx, ty), (nx, ny))

    def get_point_at_progress(self, progress: float) -> tuple[float, float]:
        """Calculates normalized (x, y) along the circuit for progress [0.0..1.0]."""
        pos, _, _ = self.get_point_and_tangent_at_progress(progress)
        return pos

    def get_transform_params(
        self, width: float, height: float, pad: float = 14.0
    ) -> tuple[float, float, float]:
        """Calculates uniform scale and centering offset to preserve true aspect ratio."""
        span_x = max(1e-4, self._max_x - self._min_x)
        span_y = max(1e-4, self._max_y - self._min_y)

        avail_w = max(20.0, width - (2.0 * pad))
        avail_h = max(20.0, height - (2.0 * pad))

        # Uniform scale (fitInView without aspect ratio distortion)
        scale = min(avail_w / span_x, avail_h / span_y)

        scaled_w = span_x * scale
        scaled_h = span_y * scale

        offset_x = pad + (avail_w - scaled_w) / 2.0 - self._min_x * scale
        offset_y = pad + (avail_h - scaled_h) / 2.0 - self._min_y * scale

        return offset_x, offset_y, scale

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # 1. Canvas background
        painter.fillRect(0, 0, int(w), int(h), QColor(THEME.BG_CARD))

        pad = 14.0
        offset_x, offset_y, scale = self.get_transform_params(w, h, pad)

        def to_screen(nx: float, ny: float) -> QPointF:
            return QPointF(offset_x + nx * scale, offset_y + ny * scale)

        # 2. Subtle circuit grid
        painter.setPen(QPen(QColor(THEME.BORDER_SUBTLE), 1, Qt.PenStyle.DotLine))
        grid_step = 60
        for gx in range(int(pad), int(w - pad), grid_step):
            painter.drawLine(gx, int(pad), gx, int(h - pad))
        for gy in range(int(pad), int(h - pad), grid_step):
            painter.drawLine(int(pad), gy, int(w - pad), gy)

        if not self._track_points:
            return

        # 3. Build closed track path
        circuit_path = QPainterPath()
        first_pt = to_screen(*self._track_points[0])
        circuit_path.moveTo(first_pt)
        for nx, ny in self._track_points[1:]:
            circuit_path.lineTo(to_screen(nx, ny))
        circuit_path.closeSubpath()

        # 4. Draw Track Ribbon
        # Outer base outline / kerb boundary
        track_bg_pen = QPen(QColor(THEME.BORDER_MUTED), 12, Qt.PenStyle.SolidLine)
        track_bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        track_bg_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(track_bg_pen)
        painter.drawPath(circuit_path)

        # Inner track tarmac surface
        track_surface_pen = QPen(QColor(THEME.BG_SURFACE_HOVER), 7, Qt.PenStyle.SolidLine)
        track_surface_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        track_surface_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(track_surface_pen)
        painter.drawPath(circuit_path)

        # Centerline racing line (dashed)
        center_pen = QPen(QColor(THEME.BORDER_MUTED), 1, Qt.PenStyle.DashLine)
        painter.setPen(center_pen)
        painter.drawPath(circuit_path)

        # 5. Start / Finish Line (Perpendicular to track tangent)
        sf_pos, _, sf_norm = self.get_point_and_tangent_at_progress(0.0)
        sf_screen = to_screen(*sf_pos)
        ribbon_half_w = 8.5

        sf_p1 = QPointF(sf_screen.x() - sf_norm[0] * ribbon_half_w, sf_screen.y() - sf_norm[1] * ribbon_half_w)
        sf_p2 = QPointF(sf_screen.x() + sf_norm[0] * ribbon_half_w, sf_screen.y() + sf_norm[1] * ribbon_half_w)

        sf_pen = QPen(QColor("#FFFFFF"), 3.5, Qt.PenStyle.SolidLine)
        sf_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(sf_pen)
        painter.drawLine(sf_p1, sf_p2)

        # S/F Label badge
        sf_badge_center = QPointF(
            sf_screen.x() + sf_norm[0] * 20.0,
            sf_screen.y() + sf_norm[1] * 20.0,
        )
        sf_badge_rect = QRectF(sf_badge_center.x() - 16, sf_badge_center.y() - 8, 32, 16)
        painter.setPen(QPen(QColor(THEME.BORDER_SUBTLE), 1))
        painter.setBrush(QBrush(QColor(THEME.BG_SURFACE_ELEVATED)))
        painter.drawRoundedRect(sf_badge_rect, 3, 3)

        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(sf_badge_rect, Qt.AlignmentFlag.AlignCenter, "S/F")

        # 6. Sector Demarcation Lines (SEC 1, SEC 2)
        frac1, frac2 = self._sector_fractions
        sec_font = QFont("Consolas", 7, QFont.Weight.Bold)
        painter.setFont(sec_font)

        # Sector 1 Boundary
        s1_pos, _, s1_norm = self.get_point_and_tangent_at_progress(frac1)
        s1_screen = to_screen(*s1_pos)
        s1_p1 = QPointF(s1_screen.x() - s1_norm[0] * ribbon_half_w, s1_screen.y() - s1_norm[1] * ribbon_half_w)
        s1_p2 = QPointF(s1_screen.x() + s1_norm[0] * ribbon_half_w, s1_screen.y() + s1_norm[1] * ribbon_half_w)

        painter.setPen(QPen(QColor(THEME.CYAN), 2.5, Qt.PenStyle.SolidLine))
        painter.drawLine(s1_p1, s1_p2)

        s1_label_rect = QRectF(s1_screen.x() + s1_norm[0] * 22.0 - 18, s1_screen.y() + s1_norm[1] * 22.0 - 8, 36, 16)
        painter.setPen(QPen(QColor(THEME.BORDER_SUBTLE), 1))
        painter.setBrush(QBrush(QColor(THEME.BG_SURFACE_ELEVATED)))
        painter.drawRoundedRect(s1_label_rect, 3, 3)
        painter.setPen(QColor(THEME.CYAN))
        painter.drawText(s1_label_rect, Qt.AlignmentFlag.AlignCenter, "SEC 1")

        # Sector 2 Boundary
        s2_pos, _, s2_norm = self.get_point_and_tangent_at_progress(frac2)
        s2_screen = to_screen(*s2_pos)
        s2_p1 = QPointF(s2_screen.x() - s2_norm[0] * ribbon_half_w, s2_screen.y() - s2_norm[1] * ribbon_half_w)
        s2_p2 = QPointF(s2_screen.x() + s2_norm[0] * ribbon_half_w, s2_screen.y() + s2_norm[1] * ribbon_half_w)

        painter.setPen(QPen(QColor(THEME.PURPLE), 2.5, Qt.PenStyle.SolidLine))
        painter.drawLine(s2_p1, s2_p2)

        s2_label_rect = QRectF(s2_screen.x() + s2_norm[0] * 22.0 - 18, s2_screen.y() + s2_norm[1] * 22.0 - 8, 36, 16)
        painter.setPen(QPen(QColor(THEME.BORDER_SUBTLE), 1))
        painter.setBrush(QBrush(QColor(THEME.BG_SURFACE_ELEVATED)))
        painter.drawRoundedRect(s2_label_rect, 3, 3)
        painter.setPen(QColor(THEME.PURPLE))
        painter.drawText(s2_label_rect, Qt.AlignmentFlag.AlignCenter, "SEC 2")

        # 7. Subtle HUD telemetry info in bottom-left
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.setPen(QColor(THEME.TEXT_MUTED))
        hud_text = f"{self._track_name.upper()}  //  {self._track_length_m:,.0f} M"
        painter.drawText(QRectF(18, h - 26, 320, 18), Qt.AlignmentFlag.AlignLeft, hud_text)

        # 8. Car Markers
        car_font = QFont("Consolas", 8, QFont.Weight.Bold)
        painter.setFont(car_font)

        for car in self._cars:
            car_nx, car_ny = self.get_point_at_progress(car.progress)
            screen_pt = to_screen(car_nx, car_ny)
            car_color = QColor(car.color_hex)

            # Selected Driver Pulsing/Highlight ring
            if car.is_selected:
                outer_glow = QColor(car_color)
                outer_glow.setAlpha(45)
                painter.setBrush(QBrush(outer_glow))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(screen_pt, 16, 16)

                glow_pen = QPen(car_color, 2, Qt.PenStyle.SolidLine)
                painter.setPen(glow_pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(screen_pt, 12, 12)

            # Car Marker Circle
            painter.setPen(QPen(QColor(THEME.BG_BASE), 2))
            painter.setBrush(QBrush(car_color))
            painter.drawEllipse(screen_pt, 5.5, 5.5)

            # Driver Number badge beside the car
            badge_rect = QRectF(screen_pt.x() + 9, screen_pt.y() - 9, 26, 18)
            painter.setPen(QPen(QColor(THEME.BORDER_SUBTLE), 1))
            painter.setBrush(QBrush(QColor(THEME.BG_SURFACE_ELEVATED)))
            painter.drawRoundedRect(badge_rect, 3, 3)

            painter.setPen(car_color)
            painter.drawText(
                badge_rect,
                Qt.AlignmentFlag.AlignCenter,
                f"#{car.driver_number:02d}",
            )


class TrackView(QFrame):
    """Container frame for the track circuit canvas."""

    def __init__(self, track_name: str = "Prototype Circuit", parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("panelFrame")
        self.setStyleSheet(
            f"""
            QFrame#panelFrame {{
                background-color: {THEME.BG_SURFACE};
                border: 1px solid {THEME.BORDER_SUBTLE};
                border-radius: 6px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # Header
        header = QHBoxLayout()
        header.setContentsMargins(2, 0, 2, 0)
        title = QLabel("CIRCUIT GPS & TRACK VISUALIZATION")
        title.setStyleSheet(
            f"font-size: 11px; font-weight: 800; letter-spacing: 1.2px; color: {THEME.TEXT_SECONDARY};"
        )
        self.track_name_label = QLabel(track_name.upper())
        self.track_name_label.setStyleSheet(
            f"font-size: 10px; font-weight: 700; letter-spacing: 1px; color: {THEME.CYAN};"
        )

        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.track_name_label)
        layout.addLayout(header)

        # Canvas
        self.canvas = TrackCircuitCanvas()
        layout.addWidget(self.canvas, 1)

    def update_cars(self, cars: list[CarMarkerData]):
        self.canvas.set_cars(cars)

    def set_track(self, track: Any):
        name = getattr(track, "name", "Prototype Circuit")
        self.track_name_label.setText(name.upper())
        self.canvas.set_track(track)
