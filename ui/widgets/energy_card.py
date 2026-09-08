"""Powertrain & Energy Storage Dashboard Card (2026 FIA Technical Regulations - Layout Scuderia).

Displays:
1. Internal Combustion Fuel mass (kg), flow rate (kg/h), and dynamic tank bar.
2. ERS 4.0 MJ Battery Depot with SOC %, energy in MJ, and linear gradient state bar.
3. Dynamic Hybrid Status Badge (MGU-K REGEN, DEPLOYING, MOM ACTIVE 350 kW, ERS STANDBY).
"""


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from ui.theme import FONT_FAMILY_MONO, THEME
from ui.view_models.race_view_model import DriverSnapshot


class EnergyCard(QFrame):
    """Powertrain & Energy Storage card showing fuel and 4.0 MJ ERS battery dynamics."""

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

        # -------------------------------------------------------------
        # Header: Title & Dynamic Hybrid Status Badge
        # -------------------------------------------------------------
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        title = QLabel("POWERTRAIN & ERS 4.0 MJ")
        title.setStyleSheet(
            f"font-size: 10px; font-weight: 800; letter-spacing: 1.1px; color: {THEME.TEXT_SECONDARY};"
        )

        self.hybrid_badge = QLabel("[ ⚡ ERS STANDBY ]")
        self.hybrid_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_hybrid_badge_style("IDLE")

        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.hybrid_badge)
        layout.addLayout(header)

        # -------------------------------------------------------------
        # Section 1: Internal Combustion Fuel
        # -------------------------------------------------------------
        fuel_section = QVBoxLayout()
        fuel_section.setSpacing(3)
        fuel_section.setContentsMargins(0, 0, 0, 0)

        fuel_header = QHBoxLayout()
        fuel_header.setContentsMargins(0, 0, 0, 0)

        lbl_fuel_title = QLabel("ICE FUEL LOAD")
        lbl_fuel_title.setStyleSheet(
            f"font-size: 8px; font-weight: 800; letter-spacing: 0.8px; color: {THEME.TEXT_MUTED};"
        )
        self.val_fuel_flow = QLabel("FLOW: 0.0 KG/H")
        self.val_fuel_flow.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 8px; font-weight: 700; color: {THEME.AMBER}; letter-spacing: 0.6px;"
        )
        fuel_header.addWidget(lbl_fuel_title)
        fuel_header.addStretch(1)
        fuel_header.addWidget(self.val_fuel_flow)
        fuel_section.addLayout(fuel_header)

        fuel_readout = QHBoxLayout()
        fuel_readout.setContentsMargins(0, 0, 0, 0)
        fuel_readout.setSpacing(4)
        fuel_readout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBaseline)

        self.val_fuel = QLabel("100.0")
        self.val_fuel.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 16px; font-weight: 700; color: {THEME.TEXT_PRIMARY};"
        )
        self.unit_fuel = QLabel("KG")
        self.unit_fuel.setStyleSheet(
            f"font-size: 9px; font-weight: 800; color: {THEME.TEXT_MUTED}; letter-spacing: 0.8px; margin-bottom: 2px;"
        )
        fuel_readout.addWidget(self.val_fuel)
        fuel_readout.addWidget(self.unit_fuel)
        fuel_readout.addStretch(1)
        fuel_section.addLayout(fuel_readout)

        # Fuel progress bar
        self.fuel_bar = QProgressBar()
        self.fuel_bar.setRange(0, 1000)  # 0.0 to 100.0 kg
        self.fuel_bar.setValue(1000)
        self.fuel_bar.setTextVisible(False)
        self.fuel_bar.setFixedHeight(4)
        self.fuel_bar.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: {THEME.BORDER_SUBTLE};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {THEME.AMBER};
                border-radius: 2px;
            }}
            """
        )
        fuel_section.addWidget(self.fuel_bar)
        layout.addLayout(fuel_section)

        # Subtle divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {THEME.BORDER_SUBTLE};")
        layout.addWidget(divider)

        # -------------------------------------------------------------
        # Section 2: ERS 4.0 MJ Battery Storage (2026 Regs)
        # -------------------------------------------------------------
        ers_section = QVBoxLayout()
        ers_section.setSpacing(3)
        ers_section.setContentsMargins(0, 0, 0, 0)

        ers_header = QHBoxLayout()
        ers_header.setContentsMargins(0, 0, 0, 0)

        lbl_ers_title = QLabel("ERS 4.0 MJ BATTERY DEPOT")
        lbl_ers_title.setStyleSheet(
            f"font-size: 8px; font-weight: 800; letter-spacing: 0.8px; color: {THEME.TEXT_MUTED};"
        )
        self.val_ers_mj = QLabel("3.40 MJ / 4.00 MJ")
        self.val_ers_mj.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 8px; font-weight: 700; color: {THEME.CYAN}; letter-spacing: 0.6px;"
        )
        ers_header.addWidget(lbl_ers_title)
        ers_header.addStretch(1)
        ers_header.addWidget(self.val_ers_mj)
        ers_section.addLayout(ers_header)

        ers_readout = QHBoxLayout()
        ers_readout.setContentsMargins(0, 0, 0, 0)
        ers_readout.setSpacing(4)
        ers_readout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBaseline)

        self.val_soc = QLabel("SOC: 85.0%")
        self.val_soc.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 16px; font-weight: 700; color: {THEME.CYAN};"
        )
        ers_readout.addWidget(self.val_soc)
        ers_readout.addStretch(1)
        ers_section.addLayout(ers_readout)

        # Dynamic Colored ERS Level Bar (Cyan-to-Purple Gradient)
        self.ers_bar = QProgressBar()
        self.ers_bar.setRange(0, 1000)  # 0.0% to 100.0%
        self.ers_bar.setValue(850)
        self.ers_bar.setTextVisible(False)
        self.ers_bar.setFixedHeight(4)
        self.ers_bar.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: {THEME.BORDER_SUBTLE};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 {THEME.CYAN}, stop:1 {THEME.PURPLE}
                );
                border-radius: 2px;
            }}
            """
        )
        ers_section.addWidget(self.ers_bar)
        layout.addLayout(ers_section)

    def _set_hybrid_badge_style(self, status: str) -> None:
        """Applies dynamic styling and text for hybrid status badge."""
        if status == "REGEN":
            self.hybrid_badge.setText("[ ⚡ MGU-K REGEN ]")
            self.hybrid_badge.setStyleSheet(
                f"""
                background-color: rgba(0, 230, 118, 0.16);
                color: {THEME.GREEN};
                border: 1px solid rgba(0, 230, 118, 0.50);
                border-radius: 3px;
                padding: 1px 5px;
                font-family: {FONT_FAMILY_MONO};
                font-size: 8px;
                font-weight: 800;
                letter-spacing: 0.6px;
                """
            )
        elif status == "MOM ACTIVE":
            self.hybrid_badge.setText("[ 🚀 MOM ACTIVE 350kW ]")
            self.hybrid_badge.setStyleSheet(
                f"""
                background-color: rgba(255, 51, 102, 0.22);
                color: {THEME.RED};
                border: 1px solid rgba(255, 51, 102, 0.75);
                border-radius: 3px;
                padding: 1px 5px;
                font-family: {FONT_FAMILY_MONO};
                font-size: 8px;
                font-weight: 900;
                letter-spacing: 0.6px;
                """
            )
        elif status == "DEPLOY":
            self.hybrid_badge.setText("[ ⚡ DEPLOYING ]")
            self.hybrid_badge.setStyleSheet(
                f"""
                background-color: rgba(0, 229, 255, 0.16);
                color: {THEME.CYAN};
                border: 1px solid rgba(0, 229, 255, 0.50);
                border-radius: 3px;
                padding: 1px 5px;
                font-family: {FONT_FAMILY_MONO};
                font-size: 8px;
                font-weight: 800;
                letter-spacing: 0.6px;
                """
            )
        else:
            self.hybrid_badge.setText("[ ⚡ ERS STANDBY ]")
            self.hybrid_badge.setStyleSheet(
                f"""
                background-color: rgba(84, 100, 127, 0.14);
                color: {THEME.TEXT_MUTED};
                border: 1px solid rgba(84, 100, 127, 0.35);
                border-radius: 3px;
                padding: 1px 5px;
                font-family: {FONT_FAMILY_MONO};
                font-size: 8px;
                font-weight: 700;
                letter-spacing: 0.6px;
                """
            )

    def update_energy(self, snapshot: DriverSnapshot | None) -> None:
        """Updates all fuel, battery, and hybrid status telemetry."""
        if snapshot is None:
            return

        # 1. Fuel Mass & Flow
        fuel_mass = snapshot.fuel
        self.val_fuel.setText(f"{fuel_mass:5.1f}")
        fuel_clamped_tenth = max(0, min(1000, int(fuel_mass * 10.0)))
        self.fuel_bar.setValue(fuel_clamped_tenth)

        flow_kgh = getattr(snapshot, "fuel_flow_kgh", 0.0)
        if flow_kgh > 0.5:
            self.val_fuel_flow.setText(f"FLOW: {flow_kgh:4.1f} KG/H")
            self.val_fuel_flow.setStyleSheet(
                f"font-family: {FONT_FAMILY_MONO}; font-size: 8px; font-weight: 700; color: {THEME.AMBER}; letter-spacing: 0.6px;"
            )
        else:
            self.val_fuel_flow.setText("FLOW: CUTOFF")
            self.val_fuel_flow.setStyleSheet(
                f"font-family: {FONT_FAMILY_MONO}; font-size: 8px; font-weight: 700; color: {THEME.TEXT_MUTED}; letter-spacing: 0.6px;"
            )

        # 2. ERS Battery SOC & Energy
        soc_pct = getattr(snapshot, "ers_soc_pct", 85.0)
        energy_mj = getattr(snapshot, "ers_energy_mj", 3.4)

        self.val_soc.setText(f"SOC: {soc_pct:4.1f}%")
        self.val_ers_mj.setText(f"{energy_mj:4.2f} / 4.00 MJ")

        soc_clamped_tenth = max(0, min(1000, int(soc_pct * 10.0)))
        self.ers_bar.setValue(soc_clamped_tenth)

        # 3. Dynamic Hybrid Status Badge
        ers_status = getattr(snapshot, "ers_status", "IDLE")
        self._set_hybrid_badge_style(ers_status)

    def update_fuel(self, snapshot: DriverSnapshot | None) -> None:
        """Backwards-compatibility alias for update_energy."""
        self.update_energy(snapshot)
