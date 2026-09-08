"""Compact Bottom Telemetry Strip (Layout Scuderia).

Hosts the 6 primary real-time metrics for the selected driver:
[ SPEED (km/h) ] [ GEAR ] [ RPM ] [ THROTTLE % ] [ BRAKE % ] [ AERO MODE (X/Z/MOM) ]
Edge-to-edge compact 88px horizontal layout without dead black boxes.
"""


from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QWidget,
)

from ui.theme import THEME
from ui.view_models.race_view_model import DriverSnapshot
from ui.widgets.telemetry_card import TelemetryCard


class TelemetryPanel(QFrame):
    """Horizontal telemetry strip displaying the 6 essential telemetry metrics."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("panelFrame")
        self.setFixedHeight(86)
        self.setStyleSheet(
            f"""
            QFrame#panelFrame {{
                background-color: {THEME.BG_SURFACE};
                border: 1px solid {THEME.BORDER_SUBTLE};
                border-radius: 6px;
            }}
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # 1. Speed (km/h)
        self.card_speed = TelemetryCard(
            label="SPEED",
            initial_value="0.0",
            unit="KM/H",
            show_bar=True,
            bar_color=THEME.CYAN,
            accent_value_color=THEME.CYAN,
        )

        # 2. Gear
        self.card_gear = TelemetryCard(
            label="GEAR",
            initial_value="N",
            unit="",
            show_bar=False,
            accent_value_color=THEME.YELLOW,
        )

        # 3. Engine RPM
        self.card_rpm = TelemetryCard(
            label="ENGINE RPM",
            initial_value="0",
            unit="RPM",
            show_bar=True,
            bar_color=THEME.PURPLE,
            accent_value_color=THEME.PURPLE,
        )

        # 4. Throttle %
        self.card_throttle = TelemetryCard(
            label="THROTTLE",
            initial_value="0.0",
            unit="%",
            show_bar=True,
            bar_color=THEME.GREEN,
            accent_value_color=THEME.GREEN,
        )

        # 5. Brake %
        self.card_brake = TelemetryCard(
            label="BRAKE",
            initial_value="0.0",
            unit="%",
            show_bar=True,
            bar_color=THEME.RED,
            accent_value_color=THEME.RED,
        )

        # 6. 2026 Aero / MOM Mode
        self.card_aero = TelemetryCard(
            label="AERO / BOOST",
            initial_value="Z-MODE",
            unit="HIGH DF",
            show_bar=False,
            accent_value_color=THEME.CYAN,
        )

        layout.addWidget(self.card_speed, stretch=18)
        layout.addWidget(self.card_gear, stretch=12)
        layout.addWidget(self.card_rpm, stretch=18)
        layout.addWidget(self.card_throttle, stretch=18)
        layout.addWidget(self.card_brake, stretch=18)
        layout.addWidget(self.card_aero, stretch=16)

    def update_telemetry(self, snapshot: DriverSnapshot | None) -> None:
        """Updates all 6 metric cards using the given driver snapshot."""
        if snapshot is None:
            self.card_speed.set_value("0.0", "KM/H", ratio=0.0)
            self.card_gear.set_value("N")
            self.card_rpm.set_value("0", "RPM", ratio=0.0)
            self.card_throttle.set_value("0.0", "%", ratio=0.0)
            self.card_brake.set_value("0.0", "%", ratio=0.0)
            self.card_aero.set_value("Z-MODE", "HIGH DF", override_color=THEME.CYAN)
            return

        # 1. Speed (km/h)
        speed_ratio = snapshot.speed / 340.0
        self.card_speed.set_value(
            f"{snapshot.speed:5.1f}",
            unit_str="KM/H",
            ratio=speed_ratio,
        )

        # 2. Gear
        self.card_gear.set_value(str(snapshot.gear))

        # 3. RPM
        rpm_ratio = snapshot.rpm / 13000.0
        self.card_rpm.set_value(
            f"{int(snapshot.rpm):,}",
            unit_str="RPM",
            ratio=rpm_ratio,
        )

        # 4. Throttle %
        throttle_pct = snapshot.throttle * 100.0
        self.card_throttle.set_value(
            f"{throttle_pct:5.1f}",
            unit_str="%",
            ratio=snapshot.throttle,
        )

        # 5. Brake %
        brake_pct = snapshot.brake * 100.0
        self.card_brake.set_value(
            f"{brake_pct:5.1f}",
            unit_str="%",
            ratio=snapshot.brake,
        )

        # 6. Active Aero & MOM State
        aero_mode = getattr(snapshot, "aero_mode", "Z-MODE")
        ers_status = getattr(snapshot, "ers_status", "IDLE")

        if ers_status == "MOM ACTIVE":
            self.card_aero.set_value(
                "MOM BOOST",
                unit_str="350 kW",
                override_color=THEME.RED,
            )
        elif aero_mode == "X-MODE":
            self.card_aero.set_value(
                "X-MODE",
                unit_str="LOW DRAG",
                override_color=THEME.YELLOW,
            )
        else:
            self.card_aero.set_value(
                "Z-MODE",
                unit_str="HIGH DF",
                override_color=THEME.CYAN,
            )
