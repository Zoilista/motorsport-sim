"""Real-time Telemetry Waveform Graph using PySide6 QPainter (Layout Scuderia).

Features:
- Spans full column width without dead black margins.
- 0 to 350 km/h calibrated engineering grid.
- Smooth anti-aliased gradient fill curve matching active driver branding.
"""

from collections.abc import Sequence

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
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

from ui.theme import FONT_FAMILY_MONO, THEME


class TelemetryGraphCanvas(QWidget):
    """QPainter canvas for plotting rolling telemetry curves."""

    def __init__(
        self,
        max_value: float = 350.0,
        min_value: float = 0.0,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.max_value = max_value
        self.min_value = min_value
        self._data: Sequence[float] = []
        self._line_color = QColor(THEME.CYAN)
        self.setMinimumHeight(130)

    def set_data(self, data: Sequence[float], color_hex: str = THEME.CYAN):
        self._data = data
        self._line_color = QColor(color_hex)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Crisp engineering margins
        left_margin = 38
        right_margin = 12
        top_margin = 10
        bottom_margin = 18

        plot_w = max(10, width - left_margin - right_margin)
        plot_h = max(10, height - top_margin - bottom_margin)

        # 1. Background
        painter.fillRect(0, 0, width, height, QColor(THEME.BG_CARD))

        # 2. Grid lines & Y-Axis labels
        grid_font = QFont("Consolas", 8)
        painter.setFont(grid_font)

        y_steps = [0, 100, 200, 300, 350]
        for val in y_steps:
            ratio = (val - self.min_value) / (self.max_value - self.min_value)
            y_pos = top_margin + plot_h * (1.0 - ratio)

            # Grid line
            painter.setPen(QPen(QColor(THEME.BORDER_SUBTLE), 1, Qt.PenStyle.DashLine))
            painter.drawLine(left_margin, int(y_pos), int(left_margin + plot_w), int(y_pos))

            # Y-axis label
            painter.setPen(QColor(THEME.TEXT_MUTED))
            painter.drawText(
                QRectF(0, y_pos - 7, left_margin - 6, 14),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                str(val),
            )

        # Vertical time dividers (every 5 seconds across a 15s window)
        painter.setPen(QPen(QColor(THEME.BORDER_SUBTLE), 1, Qt.PenStyle.DotLine))
        num_time_divs = 3
        for i in range(1, num_time_divs):
            x_pos = left_margin + (plot_w * i / num_time_divs)
            painter.drawLine(int(x_pos), top_margin, int(x_pos), int(top_margin + plot_h))

        # Time labels along the bottom
        painter.setPen(QColor(THEME.TEXT_MUTED))
        painter.drawText(
            QRectF(left_margin, height - bottom_margin + 2, 70, 14),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "-15.0s",
        )
        painter.drawText(
            QRectF(left_margin + plot_w / 2 - 35, height - bottom_margin + 2, 70, 14),
            Qt.AlignmentFlag.AlignCenter,
            "-7.5s",
        )
        painter.drawText(
            QRectF(left_margin + plot_w - 50, height - bottom_margin + 2, 50, 14),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            "0.0s",
        )

        # 3. Plot Telemetry Data Line
        if not self._data or len(self._data) < 2:
            return

        points = []
        n_points = len(self._data)
        dx = plot_w / max(1, n_points - 1)
        val_range = max(1.0, self.max_value - self.min_value)

        for i, val in enumerate(self._data):
            x = left_margin + i * dx
            clamped_val = max(self.min_value, min(self.max_value, val))
            ratio = (clamped_val - self.min_value) / val_range
            y = top_margin + plot_h * (1.0 - ratio)
            points.append(QPointF(x, y))

        # Create smooth curve path
        path = QPainterPath()
        path.moveTo(points[0])
        for pt in points[1:]:
            path.lineTo(pt)

        # Gradient fill under curve
        fill_path = QPainterPath(path)
        fill_path.lineTo(points[-1].x(), top_margin + plot_h)
        fill_path.lineTo(points[0].x(), top_margin + plot_h)
        fill_path.closeSubpath()

        grad = QLinearGradient(0, top_margin, 0, top_margin + plot_h)
        c_fill = QColor(self._line_color)
        c_fill.setAlpha(45)
        grad.setColorAt(0.0, c_fill)
        c_fill_end = QColor(self._line_color)
        c_fill_end.setAlpha(0)
        grad.setColorAt(1.0, c_fill_end)

        painter.fillPath(fill_path, grad)

        # Draw stroke
        pen = QPen(self._line_color, 2.0)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)

        # Current value marker dot on latest point
        last_pt = points[-1]
        painter.setBrush(self._line_color)
        painter.setPen(QPen(QColor(THEME.BG_BASE), 1.5))
        painter.drawEllipse(last_pt, 4, 4)


class TelemetryGraph(QFrame):
    """Wrapper frame containing the telemetry graph canvas and header stats."""

    def __init__(self, parent: QWidget | None = None):
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

        title = QLabel("SPEED TELEMETRY WAVEFORM")
        title.setStyleSheet(
            f"font-size: 11px; font-weight: 800; letter-spacing: 1.2px; color: {THEME.TEXT_SECONDARY};"
        )

        self.current_val_label = QLabel("0.0 KM/H")
        self.current_val_label.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 12px; font-weight: 700; color: {THEME.CYAN};"
        )

        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.current_val_label)
        layout.addLayout(header)

        # Canvas
        self.canvas = TelemetryGraphCanvas(max_value=350.0, min_value=0.0)
        layout.addWidget(self.canvas)

    def update_graph(self, speed_history: Sequence[float], color_hex: str = THEME.CYAN) -> None:
        """Passes the latest history buffer to the canvas."""
        self.canvas.set_data(speed_history, color_hex)
        if speed_history:
            last_speed = speed_history[-1]
            self.current_val_label.setText(f"{last_speed:5.1f} KM/H")
            self.current_val_label.setStyleSheet(
                f"font-family: {FONT_FAMILY_MONO}; font-size: 12px; font-weight: 700; color: {color_hex};"
            )
