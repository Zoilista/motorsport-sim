"""Modern Ground-Effect F1 2D Chassis & Telemetry Visualization (QPainter)."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QWidget

from ui.theme import THEME


class CarSetupView(QWidget):
    """Renders a technical top-down schematic of a modern ground-effect F1 car."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumSize(380, 480)

        self._driver_name: str = "Driver A"
        self._driver_number: int = 7
        self._color_hex: str = THEME.CYAN

        self._tyre_temps = {"FL": 80.0, "FR": 80.0, "RL": 80.0, "RR": 80.0}
        self._tyre_wears = {"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0}

    def set_driver(self, name: str, number: int, color_hex: str) -> None:
        self._driver_name = name
        self._driver_number = number
        self._color_hex = color_hex
        self.update()

    def set_tyre_telemetry(self, temp: float, wear: float) -> None:
        for pos in self._tyre_temps:
            self._tyre_temps[pos] = temp
            self._tyre_wears[pos] = wear
        self.update()

    def set_tyre_telemetry_4w(
        self,
        fl_temp: float,
        fr_temp: float,
        rl_temp: float,
        rr_temp: float,
        fl_wear: float,
        fr_wear: float,
        rl_wear: float,
        rr_wear: float,
    ) -> None:
        self._tyre_temps["FL"] = fl_temp
        self._tyre_temps["FR"] = fr_temp
        self._tyre_temps["RL"] = rl_temp
        self._tyre_temps["RR"] = rr_temp
        self._tyre_wears["FL"] = fl_wear
        self._tyre_wears["FR"] = fr_wear
        self._tyre_wears["RL"] = rl_wear
        self._tyre_wears["RR"] = rr_wear
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # Dark Technical Canvas Background
        painter.fillRect(0, 0, int(w), int(h), QColor("#080C12"))

        # Engineering Grid with subtle coordinates
        grid_pen = QPen(QColor("#131C28"), 1, Qt.PenStyle.DotLine)
        painter.setPen(grid_pen)
        grid_step = 28
        for x in range(0, int(w), grid_step):
            painter.drawLine(x, 0, x, int(h))
        for y in range(0, int(h), grid_step):
            painter.drawLine(0, y, int(w), y)

        cx = w / 2.0
        cy = h / 2.0 - 8.0

        accent = QColor(self._color_hex)
        accent_alpha30 = QColor(accent)
        accent_alpha30.setAlpha(30)
        carbon_edge = QColor("#222F42")
        tire_rubber = QColor("#090C10")
        susp_color = QColor("#303F54")

        # Proportions: Modern Ground-Effect F1 (Long Wheelbase ~3600mm)
        front_axle_y = cy - 118.0
        rear_axle_y = cy + 112.0
        track_half_w = 96.0

        wheel_w = 32.0
        wheel_h = 66.0

        wheel_rects = {
            "FL": QRectF(cx - track_half_w - wheel_w / 2.0, front_axle_y - wheel_h / 2.0, wheel_w, wheel_h),
            "FR": QRectF(cx + track_half_w - wheel_w / 2.0, front_axle_y - wheel_h / 2.0, wheel_w, wheel_h),
            "RL": QRectF(cx - track_half_w - wheel_w / 2.0, rear_axle_y - wheel_h / 2.0, wheel_w, wheel_h),
            "RR": QRectF(cx + track_half_w - wheel_w / 2.0, rear_axle_y - wheel_h / 2.0, wheel_w, wheel_h),
        }

        # -------------------------------------------------------------
        # 1. GROUND EFFECT FLOOR EDGES & VENTURI CHANNELS (Underbody)
        # -------------------------------------------------------------
        floor_path = QPainterPath()
        floor_path.moveTo(cx - 38.0, cy - 80.0)
        floor_path.lineTo(cx - 58.0, cy - 40.0)  # Floor leading edge
        floor_path.lineTo(cx - 60.0, cy + 45.0)  # Outer floor edge
        floor_path.lineTo(cx - 52.0, cy + 95.0)  # Rear diffuser expansion
        floor_path.lineTo(cx + 52.0, cy + 95.0)
        floor_path.lineTo(cx + 60.0, cy + 45.0)
        floor_path.lineTo(cx + 58.0, cy - 40.0)
        floor_path.lineTo(cx + 38.0, cy - 80.0)
        floor_path.closeSubpath()

        painter.setPen(QPen(QColor("#1A2433"), 1.5))
        painter.setBrush(QBrush(QColor("#0B0F16")))
        painter.drawPath(floor_path)

        # Floor edge winglets / longitudinal strakes
        painter.setPen(QPen(accent, 1))
        painter.drawLine(QPointF(cx - 59.0, cy - 20.0), QPointF(cx - 59.0, cy + 40.0))
        painter.drawLine(QPointF(cx + 59.0, cy - 20.0), QPointF(cx + 59.0, cy + 40.0))

        # -------------------------------------------------------------
        # 2. DOUBLE WISHBONE SUSPENSION & STEERING RODS
        # -------------------------------------------------------------
        painter.setPen(QPen(susp_color, 1.8))
        # Front Suspension (Push-rod layout)
        painter.drawLine(QPointF(cx - 16, front_axle_y - 18), QPointF(cx - track_half_w + 12, front_axle_y - 12))
        painter.drawLine(QPointF(cx - 16, front_axle_y + 14), QPointF(cx - track_half_w + 12, front_axle_y + 12))
        painter.drawLine(QPointF(cx - 16, front_axle_y - 4), QPointF(cx - track_half_w + 12, front_axle_y))  # Pushrod
        painter.drawLine(QPointF(cx + 16, front_axle_y - 18), QPointF(cx + track_half_w - 12, front_axle_y - 12))
        painter.drawLine(QPointF(cx + 16, front_axle_y + 14), QPointF(cx + track_half_w - 12, front_axle_y + 12))
        painter.drawLine(QPointF(cx + 16, front_axle_y - 4), QPointF(cx + track_half_w - 12, front_axle_y))

        # Rear Suspension (Pull-rod layout)
        painter.drawLine(QPointF(cx - 18, rear_axle_y - 20), QPointF(cx - track_half_w + 12, rear_axle_y - 12))
        painter.drawLine(QPointF(cx - 18, rear_axle_y + 18), QPointF(cx - track_half_w + 12, rear_axle_y + 12))
        painter.drawLine(QPointF(cx + 18, rear_axle_y - 20), QPointF(cx + track_half_w - 12, rear_axle_y - 12))
        painter.drawLine(QPointF(cx + 18, rear_axle_y + 18), QPointF(cx + track_half_w - 12, rear_axle_y + 12))

        # -------------------------------------------------------------
        # 3. OPEN WHEELS (18-inch rims with aero covers)
        # -------------------------------------------------------------
        for pos_key, rect in wheel_rects.items():
            # Tire carcass
            painter.setPen(QPen(accent, 1.2))
            painter.setBrush(QBrush(tire_rubber))
            painter.drawRoundedRect(rect, 7, 7)

            # Aero Wheel Cover Disc
            disc_rect = QRectF(rect.x() + 5, rect.y() + 8, rect.width() - 10, rect.height() - 16)
            painter.setPen(QPen(QColor("#1E2838"), 1))
            painter.setBrush(QBrush(QColor("#111822")))
            painter.drawRoundedRect(disc_rect, 4, 4)

            # Wheel Nut Center
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(accent))
            painter.drawEllipse(rect.center(), 3.5, 3.5)

            # Front Wheel Wake Deflectors (Brows)
            if "F" in pos_key:
                brow_x = rect.right() + 3 if "L" in pos_key else rect.left() - 7
                brow_rect = QRectF(brow_x, rect.top() + 6, 4, 28)
                painter.setBrush(QBrush(carbon_edge))
                painter.drawRoundedRect(brow_rect, 2, 2)

        # -------------------------------------------------------------
        # 4. CHASSIS MONOCOQUE & SCULPTED COKE-BOTTLE SIDEPODS
        # -------------------------------------------------------------
        nose_tip_y = cy - 185.0
        chassis_path = QPainterPath()

        # Start at nose tip
        chassis_path.moveTo(cx, nose_tip_y)
        # Organic curved nose cone
        chassis_path.cubicTo(QPointF(cx + 6, nose_tip_y + 35), QPointF(cx + 14, cy - 110), QPointF(cx + 16, cy - 75))
        # Sidepod undercut entrance
        chassis_path.lineTo(cx + 42, cy - 42)
        # Sidepod maximum width (downwash shoulder)
        chassis_path.cubicTo(QPointF(cx + 46, cy - 10), QPointF(cx + 44, cy + 25), QPointF(cx + 34, cy + 60))
        # Coke-bottle sweep narrowing inwards
        chassis_path.cubicTo(QPointF(cx + 24, cy + 85), QPointF(cx + 15, cy + 120), QPointF(cx + 12, cy + 150))
        # Rear crash structure & exhaust exit
        chassis_path.lineTo(cx - 12, cy + 150)
        # Left Coke-bottle sweep
        chassis_path.cubicTo(QPointF(cx - 15, cy + 120), QPointF(cx - 24, cy + 85), QPointF(cx - 34, cy + 60))
        chassis_path.cubicTo(QPointF(cx - 44, cy + 25), QPointF(cx - 46, cy - 10), QPointF(cx - 42, cy - 42))
        chassis_path.lineTo(cx - 16, cy - 75)
        chassis_path.cubicTo(QPointF(cx - 14, cy - 110), QPointF(cx - 6, nose_tip_y + 35), QPointF(cx, nose_tip_y))
        chassis_path.closeSubpath()

        # Bodywork Gradient Fill (Metallic carbon depth)
        body_grad = QLinearGradient(cx - 50, cy, cx + 50, cy)
        body_grad.setColorAt(0.0, QColor("#101620"))
        body_grad.setColorAt(0.2, QColor("#1A2230"))
        body_grad.setColorAt(0.5, QColor("#263347"))
        body_grad.setColorAt(0.8, QColor("#1A2230"))
        body_grad.setColorAt(1.0, QColor("#101620"))

        painter.setPen(QPen(carbon_edge, 1.8))
        painter.setBrush(body_grad)
        painter.drawPath(chassis_path)

        # Radiator cooling louvres on sidepods
        painter.setPen(QPen(QColor("#121924"), 1.2))
        for ly in range(int(cy - 20), int(cy + 30), 8):
            painter.drawLine(QPointF(cx - 36, ly), QPointF(cx - 22, ly + 2))
            painter.drawLine(QPointF(cx + 36, ly), QPointF(cx + 22, ly + 2))

        # -------------------------------------------------------------
        # 5. MODERN 3D FRONT WING & SCULPTED ENDPLATES
        # -------------------------------------------------------------
        fw_y = nose_tip_y + 14.0

        # Multi-element curved front wing flap
        fw_path = QPainterPath()
        fw_path.moveTo(cx - 96, fw_y + 16)
        fw_path.cubicTo(QPointF(cx - 50, fw_y - 2), QPointF(cx - 15, fw_y - 12), QPointF(cx, fw_y - 14))
        fw_path.cubicTo(QPointF(cx + 15, fw_y - 14), QPointF(cx + 50, fw_y - 2), QPointF(cx + 96, fw_y + 16))
        fw_path.lineTo(cx + 92, fw_y + 26)
        fw_path.cubicTo(QPointF(cx + 45, fw_y + 8), QPointF(cx + 15, fw_y), QPointF(cx, fw_y))
        fw_path.cubicTo(QPointF(cx - 15, fw_y), QPointF(cx - 45, fw_y + 8), QPointF(cx - 92, fw_y + 26))
        fw_path.closeSubpath()

        painter.setPen(QPen(accent, 1.5))
        painter.setBrush(QBrush(QColor("#0E141D")))
        painter.drawPath(fw_path)

        # Wing Endplates with outer curved dive-planes
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(accent))
        painter.drawRoundedRect(QRectF(cx - 98, fw_y - 4, 5, 34), 2, 2)
        painter.drawRoundedRect(QRectF(cx + 93, fw_y - 4, 5, 34), 2, 2)

        # -------------------------------------------------------------
        # 6. COCKPIT, DRIVER HELMET & MODERN HALO SAFETY BAR
        # -------------------------------------------------------------
        # Cockpit well
        cockpit_rect = QRectF(cx - 11, cy - 62, 22, 54)
        painter.setPen(QPen(QColor("#05080C"), 1.5))
        painter.setBrush(QBrush(QColor("#070B10")))
        painter.drawRoundedRect(cockpit_rect, 9, 9)

        # Driver Helmet
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(accent))
        painter.drawEllipse(QRectF(cx - 6, cy - 42, 12, 14))

        # Modern Halo Protection Structure (Triangular wishbone halo)
        halo = QPainterPath()
        halo.moveTo(cx, cy - 58)  # Forward center mounting strut
        halo.lineTo(cx + 13, cy - 26)  # Right hoop anchor
        halo.lineTo(cx + 10, cy - 24)
        halo.lineTo(cx, cy - 54)
        halo.lineTo(cx - 10, cy - 24)
        halo.lineTo(cx - 13, cy - 26)  # Left hoop anchor
        halo.closeSubpath()

        painter.setPen(QPen(QColor("#0F151E"), 1))
        painter.setBrush(QBrush(accent))
        painter.drawPath(halo)

        # Airbox / Engine Intake
        airbox_rect = QRectF(cx - 7, cy - 18, 14, 16)
        painter.setPen(QPen(carbon_edge, 1.5))
        painter.setBrush(QBrush(QColor("#090C12")))
        painter.drawRoundedRect(airbox_rect, 4, 4)

        # Aerodynamic Dorsal Shark Fin
        painter.setPen(QPen(accent, 2))
        painter.drawLine(QPointF(cx, cy - 2), QPointF(cx, cy + 125))

        # -------------------------------------------------------------
        # 7. MODERN SWAN-NECK REAR WING & DRS BEAM WING
        # -------------------------------------------------------------
        rw_y = rear_axle_y + 40.0

        # Beam wing below main plane
        painter.setPen(QPen(carbon_edge, 2))
        painter.drawLine(QPointF(cx - 45, rw_y - 8), QPointF(cx + 45, rw_y - 8))

        # Mainplane (Curved profile)
        rw_rect = QRectF(cx - 76, rw_y, 152, 18)
        painter.setPen(QPen(accent, 1.5))
        painter.setBrush(QBrush(QColor("#0F141E")))
        painter.drawRoundedRect(rw_rect, 3, 3)

        # DRS Flap Actuator Pod (Center)
        painter.setBrush(QBrush(accent))
        painter.drawRoundedRect(QRectF(cx - 4, rw_y - 3, 8, 12), 2, 2)

        # Curved Modern Endplates (F1 Ground-Effect curved styling)
        ep_left = QPainterPath()
        ep_left.moveTo(cx - 78, rw_y - 8)
        ep_left.cubicTo(QPointF(cx - 82, rw_y + 5), QPointF(cx - 80, rw_y + 20), QPointF(cx - 74, rw_y + 32))
        ep_left.lineTo(cx - 70, rw_y + 30)
        ep_left.cubicTo(QPointF(cx - 75, rw_y + 18), QPointF(cx - 77, rw_y + 5), QPointF(cx - 74, rw_y - 8))
        ep_left.closeSubpath()

        ep_right = QPainterPath()
        ep_right.moveTo(cx + 78, rw_y - 8)
        ep_right.cubicTo(QPointF(cx + 82, rw_y + 5), QPointF(cx + 80, rw_y + 20), QPointF(cx + 74, rw_y + 32))
        ep_right.lineTo(cx + 70, rw_y + 30)
        ep_right.cubicTo(QPointF(cx + 75, rw_y + 18), QPointF(cx + 77, rw_y + 5), QPointF(cx + 74, rw_y - 8))
        ep_right.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(accent))
        painter.drawPath(ep_left)
        painter.drawPath(ep_right)

        # -------------------------------------------------------------
        # 8. DRIVER NUMBER BADGE ON NOSE
        # -------------------------------------------------------------
        no_font = QFont("Consolas", 12, QFont.Weight.Bold)
        painter.setFont(no_font)
        painter.setPen(accent)
        painter.drawText(
            QRectF(cx - 20, nose_tip_y + 40, 40, 22),
            Qt.AlignmentFlag.AlignCenter,
            f"#{self._driver_number:02d}",
        )

        # -------------------------------------------------------------
        # 9. LIVE WHEEL TELEMETRY BADGES (Glassmorphism telemetry cards)
        # -------------------------------------------------------------
        badge_font_val = QFont("Consolas", 8, QFont.Weight.Bold)
        badge_font_lbl = QFont("Segoe UI", 7, QFont.Weight.Bold)

        def draw_tyre_hud(pos_key: str, box_rect: QRectF, title: str, is_right: bool):
            temp = self._tyre_temps.get(pos_key, 80.0)
            wear = self._tyre_wears.get(pos_key, 0.0)

            # Thermal color coding
            if temp < 88.0:
                t_color = QColor(THEME.CYAN)
            elif 88.0 <= temp <= 106.0:
                t_color = QColor(THEME.GREEN)
            elif 106.0 < temp <= 116.0:
                t_color = QColor(THEME.AMBER)
            else:
                t_color = QColor(THEME.RED)

            # Card background
            painter.setPen(QPen(QColor("#1B2636"), 1))
            painter.setBrush(QBrush(QColor("#0B1017")))
            painter.drawRoundedRect(box_rect, 5, 5)

            # Left accent stripe
            stripe_x = box_rect.right() - 3 if is_right else box_rect.left()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(t_color))
            painter.drawRoundedRect(QRectF(stripe_x, box_rect.top() + 4, 3, box_rect.height() - 8), 1, 1)

            align = Qt.AlignmentFlag.AlignRight if is_right else Qt.AlignmentFlag.AlignLeft
            pad_x = 10 if not is_right else 8

            # Position Label
            painter.setFont(badge_font_lbl)
            painter.setPen(QColor(THEME.TEXT_MUTED))
            painter.drawText(
                QRectF(box_rect.x() + pad_x, box_rect.y() + 4, box_rect.width() - 16, 12),
                align,
                title,
            )

            # Temp
            painter.setFont(badge_font_val)
            painter.setPen(t_color)
            painter.drawText(
                QRectF(box_rect.x() + pad_x, box_rect.y() + 18, box_rect.width() - 16, 14),
                align,
                f"{temp:4.1f} °C",
            )

            # Wear
            painter.setFont(badge_font_lbl)
            painter.setPen(QColor(THEME.TEXT_SECONDARY) if wear < 0.25 else QColor(THEME.AMBER))
            painter.drawText(
                QRectF(box_rect.x() + pad_x, box_rect.y() + 32, box_rect.width() - 16, 12),
                align,
                f"WEAR {wear * 100.0:3.1f}%",
            )

        box_w = 74.0
        box_h = 48.0

        # Draw badges with plenty of clearance from wheel contours
        draw_tyre_hud("FL", QRectF(6, front_axle_y - box_h / 2.0, box_w, box_h), "FL TYRE", is_right=False)
        draw_tyre_hud("FR", QRectF(w - 6 - box_w, front_axle_y - box_h / 2.0, box_w, box_h), "FR TYRE", is_right=True)
        draw_tyre_hud("RL", QRectF(6, rear_axle_y - box_h / 2.0, box_w, box_h), "RL TYRE", is_right=False)
        draw_tyre_hud("RR", QRectF(w - 6 - box_w, rear_axle_y - box_h / 2.0, box_w, box_h), "RR TYRE", is_right=True)

        # -------------------------------------------------------------
        # 10. CHASSIS BANNER FOOTER
        # -------------------------------------------------------------
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(accent)
        painter.drawText(
            QRectF(10, h - 26, w - 20, 18),
            Qt.AlignmentFlag.AlignCenter,
            f"● GROUND-EFFECT AERO CHASSIS // #{self._driver_number:02d} {self._driver_name.upper()}",
        )
