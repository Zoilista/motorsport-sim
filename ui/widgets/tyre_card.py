"""Tyre Telemetry Status Card (Physical 4-Wheel Dynamic Thermal & Wear Monitor - Layout Scuderia).

Features:
- High-contrast, collision-free header with compound badge and thermal/pit status.
- 2x2 grid representing FL, FR, RL, RR tyres with calibrated dynamic thermal color coding.
- Stint age and pit-stop count tracking.
"""


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.theme import FONT_FAMILY_MONO, THEME
from ui.view_models.race_view_model import DriverSnapshot


class SingleTyreWidget(QFrame):
    """Visual widget representing a single tyre (temperature and wear with dynamic thermal color coding)."""

    def __init__(self, position_name: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {THEME.BG_BASE};
                border: 1px solid {THEME.BORDER_SUBTLE};
                border-radius: 4px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(2)

        lbl_pos = QLabel(position_name)
        lbl_pos.setStyleSheet(
            f"font-size: 8px; font-weight: 800; color: {THEME.TEXT_MUTED}; letter-spacing: 0.8px;"
        )

        val_row = QHBoxLayout()
        val_row.setContentsMargins(0, 0, 0, 0)
        val_row.setSpacing(4)

        self.val_temp = QLabel("80.0 °C")
        self.val_temp.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 12px; font-weight: 700; color: {THEME.CYAN};"
        )

        self.val_wear = QLabel("W: 0.0%")
        self.val_wear.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.val_wear.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 9px; font-weight: 600; color: {THEME.TEXT_MUTED};"
        )

        val_row.addWidget(self.val_temp)
        val_row.addStretch(1)
        val_row.addWidget(self.val_wear)

        layout.addWidget(lbl_pos)
        layout.addLayout(val_row)

    def set_values(self, temp: float, wear: float):
        # Dynamic thermal color coding
        if temp < 88.0:
            temp_color = THEME.CYAN  # Cold / Warming
        elif 88.0 <= temp <= 106.0:
            temp_color = THEME.GREEN  # Optimal window
        elif 106.0 < temp <= 116.0:
            temp_color = THEME.AMBER  # High thermal load
        else:
            temp_color = THEME.RED  # Overheating

        # Wear color coding
        wear_pct = wear * 100.0
        if wear_pct < 15.0:
            wear_color = THEME.TEXT_MUTED
        elif wear_pct < 40.0:
            wear_color = THEME.AMBER
        else:
            wear_color = THEME.RED

        self.val_temp.setText(f"{temp:4.1f} °C")
        self.val_temp.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 12px; font-weight: 700; color: {temp_color};"
        )

        self.val_wear.setText(f"W: {wear_pct:4.1f}%")
        self.val_wear.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 9px; font-weight: 600; color: {wear_color};"
        )


class TyreCard(QFrame):
    """Card displaying live 4-wheel tyre telemetry with physical thermal tracking."""

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
        # Header Row 1: Title + Compound Badge
        # -------------------------------------------------------------
        header_row1 = QHBoxLayout()
        header_row1.setContentsMargins(0, 0, 0, 0)

        title = QLabel("TYRE SYSTEM MONITOR")
        title.setStyleSheet(
            f"font-size: 10px; font-weight: 800; letter-spacing: 1.1px; color: {THEME.TEXT_SECONDARY};"
        )

        self.compound_badge = QLabel("MEDIUM [M]")
        self.compound_badge.setStyleSheet(
            f"""
            background-color: rgba(255, 214, 0, 0.18);
            color: #FFD600;
            border: 1px solid #FFD600;
            border-radius: 3px;
            padding: 1px 6px;
            font-size: 9px;
            font-weight: 800;
            font-family: {FONT_FAMILY_MONO};
            letter-spacing: 0.8px;
            """
        )

        header_row1.addWidget(title)
        header_row1.addStretch(1)
        header_row1.addWidget(self.compound_badge)
        layout.addLayout(header_row1)

        # -------------------------------------------------------------
        # Header Row 2: Stint Tracker + Thermal Status Badge
        # -------------------------------------------------------------
        header_row2 = QHBoxLayout()
        header_row2.setContentsMargins(0, 0, 0, 0)

        self.stint_tag = QLabel("AGE: L0 • 0 STOPS")
        self.stint_tag.setStyleSheet(
            f"""
            font-family: {FONT_FAMILY_MONO};
            font-size: 9px;
            font-weight: 700;
            color: {THEME.TEXT_MUTED};
            """
        )

        self.status_tag = QLabel("OPTIMAL WINDOW")
        self.status_tag.setStyleSheet(
            f"""
            background-color: rgba(0, 230, 118, 0.12);
            color: {THEME.GREEN};
            border: 1px solid rgba(0, 230, 118, 0.35);
            border-radius: 3px;
            padding: 1px 6px;
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.6px;
            """
        )

        header_row2.addWidget(self.stint_tag)
        header_row2.addStretch(1)
        header_row2.addWidget(self.status_tag)
        layout.addLayout(header_row2)

        # -------------------------------------------------------------
        # 2x2 Grid of Tyres (FL, FR, RL, RR)
        # -------------------------------------------------------------
        grid = QGridLayout()
        grid.setSpacing(6)

        self.tyre_fl = SingleTyreWidget("FL • FRONT LEFT")
        self.tyre_fr = SingleTyreWidget("FR • FRONT RIGHT")
        self.tyre_rl = SingleTyreWidget("RL • REAR LEFT")
        self.tyre_rr = SingleTyreWidget("RR • REAR RIGHT")

        grid.addWidget(self.tyre_fl, 0, 0)
        grid.addWidget(self.tyre_fr, 0, 1)
        grid.addWidget(self.tyre_rl, 1, 0)
        grid.addWidget(self.tyre_rr, 1, 1)

        layout.addLayout(grid)

    def update_tyres(self, snapshot: DriverSnapshot | None) -> None:
        if snapshot is None:
            return

        fl_t = getattr(snapshot, "fl_temp", snapshot.tyre_temperature)
        fr_t = getattr(snapshot, "fr_temp", snapshot.tyre_temperature)
        rl_t = getattr(snapshot, "rl_temp", snapshot.tyre_temperature)
        rr_t = getattr(snapshot, "rr_temp", snapshot.tyre_temperature)

        fl_w = getattr(snapshot, "fl_wear", snapshot.tyre_wear)
        fr_w = getattr(snapshot, "fr_wear", snapshot.tyre_wear)
        rl_w = getattr(snapshot, "rl_wear", snapshot.tyre_wear)
        rr_w = getattr(snapshot, "rr_wear", snapshot.tyre_wear)

        self.tyre_fl.set_values(fl_t, fl_w)
        self.tyre_fr.set_values(fr_t, fr_w)
        self.tyre_rl.set_values(rl_t, rl_w)
        self.tyre_rr.set_values(rr_t, rr_w)

        # Update compound badge
        comp_name = getattr(snapshot, "compound", "Medium")
        comp_code = getattr(snapshot, "compound_code", "M")
        comp_col = getattr(snapshot, "compound_color", "#FFD600")
        self.compound_badge.setText(f"{comp_name.upper()} [{comp_code}]")
        self.compound_badge.setStyleSheet(
            f"""
            background-color: {comp_col}22;
            color: {comp_col};
            border: 1px solid {comp_col};
            border-radius: 3px;
            padding: 1px 6px;
            font-size: 9px;
            font-weight: 800;
            font-family: {FONT_FAMILY_MONO};
            letter-spacing: 0.8px;
            """
        )

        # Update stint age tag
        laps_on_set = getattr(snapshot, "laps_on_set", 0)
        pit_stops = getattr(snapshot, "pit_stops", 0)
        stop_txt = f"{pit_stops} STOP" if pit_stops == 1 else f"{pit_stops} STOPS"
        self.stint_tag.setText(f"AGE: L{laps_on_set} • {stop_txt}")

        # Update status tag based on pit lane or temperature
        in_pit = getattr(snapshot, "in_pit_lane", False)
        pit_state = getattr(snapshot, "pit_state", "RACING")

        if in_pit:
            if pit_state == "IN_BOX_STOP":
                self.status_tag.setText("BOX STOP (2.4s)")
                self.status_tag.setStyleSheet(
                    f"""
                    background-color: rgba(255, 51, 102, 0.20);
                    color: {THEME.RED};
                    border: 1px solid {THEME.RED};
                    border-radius: 3px;
                    padding: 1px 6px;
                    font-size: 9px;
                    font-weight: 800;
                    letter-spacing: 0.6px;
                    """
                )
            else:
                self.status_tag.setText("PIT LANE (80 KM/H)")
                self.status_tag.setStyleSheet(
                    f"""
                    background-color: rgba(255, 159, 28, 0.20);
                    color: {THEME.AMBER};
                    border: 1px solid {THEME.AMBER};
                    border-radius: 3px;
                    padding: 1px 6px;
                    font-size: 9px;
                    font-weight: 800;
                    letter-spacing: 0.6px;
                    """
                )
            return

        avg_temp = (fl_t + fr_t + rl_t + rr_t) / 4.0
        if avg_temp < 88.0:
            self.status_tag.setText("COLD // WARMING")
            self.status_tag.setStyleSheet(
                f"""
                background-color: rgba(0, 229, 255, 0.12);
                color: {THEME.CYAN};
                border: 1px solid rgba(0, 229, 255, 0.35);
                border-radius: 3px;
                padding: 1px 6px;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 0.6px;
                """
            )
        elif 88.0 <= avg_temp <= 106.0:
            self.status_tag.setText("OPTIMAL WINDOW")
            self.status_tag.setStyleSheet(
                f"""
                background-color: rgba(0, 230, 118, 0.12);
                color: {THEME.GREEN};
                border: 1px solid rgba(0, 230, 118, 0.35);
                border-radius: 3px;
                padding: 1px 6px;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 0.6px;
                """
            )
        elif 106.0 < avg_temp <= 116.0:
            self.status_tag.setText("HIGH THERMAL LOAD")
            self.status_tag.setStyleSheet(
                f"""
                background-color: rgba(255, 159, 28, 0.12);
                color: {THEME.AMBER};
                border: 1px solid rgba(255, 159, 28, 0.35);
                border-radius: 3px;
                padding: 1px 6px;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 0.6px;
                """
            )
        else:
            self.status_tag.setText("OVERHEATING // DEG")
            self.status_tag.setStyleSheet(
                f"""
                background-color: rgba(255, 51, 102, 0.14);
                color: {THEME.RED};
                border: 1px solid rgba(255, 51, 102, 0.4);
                border-radius: 3px;
                padding: 1px 6px;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 0.6px;
                """
            )
