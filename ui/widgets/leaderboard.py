"""Leaderboard Widget with Interactive Driver Selection."""


from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.theme import FONT_FAMILY_MONO, THEME
from ui.view_models.race_view_model import LeaderboardEntry


class LeaderboardRowWidget(QFrame):
    """Clickable row representing a driver's standing."""

    clicked = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.driver_name = ""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(10, 6, 10, 6)
        self._layout.setSpacing(10)

        # 1. Position Rank
        self.pos_label = QLabel("P1")
        self.pos_label.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 13px; font-weight: 800; color: {THEME.TEXT_PRIMARY}; min-width: 22px;"
        )

        # 2. Car Number Badge
        self.num_badge = QLabel("#00")
        self.num_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.num_badge.setFixedSize(30, 22)
        self.num_badge.setStyleSheet(
            f"""
            background-color: rgba(0, 229, 255, 0.15);
            color: {THEME.CYAN};
            border: 1px solid rgba(0, 229, 255, 0.4);
            border-radius: 3px;
            font-family: {FONT_FAMILY_MONO};
            font-size: 11px;
            font-weight: 800;
            """
        )

        # 2b. Tyre Compound Pill Badge
        self.compound_badge = QLabel("M")
        self.compound_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.compound_badge.setFixedSize(22, 22)
        self.compound_badge.setStyleSheet(
            f"""
            background-color: rgba(255, 214, 0, 0.18);
            color: #FFD600;
            border: 1.5px solid #FFD600;
            border-radius: 11px;
            font-family: {FONT_FAMILY_MONO};
            font-size: 11px;
            font-weight: 900;
            """
        )

        # 3. Driver Name & Lap
        name_lap_layout = QVBoxLayout()
        name_lap_layout.setSpacing(1)
        name_lap_layout.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLabel("Driver")
        self.name_label.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {THEME.TEXT_PRIMARY};"
        )
        self.lap_label = QLabel("LAP 01")
        self.lap_label.setStyleSheet(
            f"font-size: 10px; font-weight: 600; color: {THEME.TEXT_MUTED}; font-family: {FONT_FAMILY_MONO};"
        )
        name_lap_layout.addWidget(self.name_label)
        name_lap_layout.addWidget(self.lap_label)

        # 4. Sector Badge
        self.sector_badge = QLabel("S1")
        self.sector_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sector_badge.setFixedSize(28, 20)
        self.sector_badge.setStyleSheet(
            f"""
            background-color: {THEME.BG_BASE};
            color: {THEME.TEXT_SECONDARY};
            border: 1px solid {THEME.BORDER_MUTED};
            border-radius: 3px;
            font-size: 10px;
            font-weight: 700;
            font-family: {FONT_FAMILY_MONO};
            """
        )

        # 5. 2026 Manual Override Mode (MOM) Indicator Badge
        self.ovr_badge = QLabel("OVR READY")
        self.ovr_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ovr_badge.setStyleSheet(
            f"""
            background-color: rgba(255, 159, 28, 0.20);
            color: {THEME.AMBER};
            border: 1px solid rgba(255, 159, 28, 0.70);
            border-radius: 3px;
            padding: 2px 5px;
            font-size: 9px;
            font-weight: 800;
            font-family: {FONT_FAMILY_MONO};
            letter-spacing: 0.5px;
            """
        )
        self.ovr_badge.hide()

        # 6. Gap & Speed (Right aligned)
        timing_layout = QVBoxLayout()
        timing_layout.setSpacing(1)
        timing_layout.setContentsMargins(0, 0, 0, 0)
        timing_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.gap_label = QLabel("LEADER")
        self.gap_label.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 12px; font-weight: 700; color: {THEME.GREEN};"
        )
        self.speed_label = QLabel("0.0 KM/H")
        self.speed_label.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 10px; font-weight: 600; color: {THEME.TEXT_MUTED};"
        )
        timing_layout.addWidget(self.gap_label)
        timing_layout.addWidget(self.speed_label)

        self._layout.addWidget(self.pos_label)
        self._layout.addWidget(self.num_badge)
        self._layout.addWidget(self.compound_badge)
        self._layout.addLayout(name_lap_layout)
        self._layout.addStretch(1)
        self._layout.addWidget(self.ovr_badge)
        self._layout.addWidget(self.sector_badge)
        self._layout.addLayout(timing_layout)

    def mousePressEvent(self, event):
        if self.driver_name:
            self.clicked.emit(self.driver_name)
        super().mousePressEvent(event)

    def update_entry(self, entry: LeaderboardEntry):
        self.driver_name = entry.driver_name
        self.pos_label.setText(f"P{entry.rank}")
        self.num_badge.setText(f"#{entry.driver_number:02d}")
        self.num_badge.setStyleSheet(
            f"""
            background-color: {entry.driver_color}22;
            color: {entry.driver_color};
            border: 1px solid {entry.driver_color}77;
            border-radius: 3px;
            font-family: {FONT_FAMILY_MONO};
            font-size: 11px;
            font-weight: 800;
            """
        )

        # Compound Pill Badge styling
        comp_code = getattr(entry, "compound_code", "M")
        comp_col = getattr(entry, "compound_color", "#FFD600")
        self.compound_badge.setText(comp_code)
        self.compound_badge.setStyleSheet(
            f"""
            background-color: {comp_col}24;
            color: {comp_col};
            border: 1.5px solid {comp_col};
            border-radius: 11px;
            font-family: {FONT_FAMILY_MONO};
            font-size: 11px;
            font-weight: 900;
            """
        )

        self.name_label.setText(entry.driver_name)

        # Stint & pit stop tracker in lap label
        laps_on_set = getattr(entry, "laps_on_set", 0)
        pit_stops = getattr(entry, "pit_stops", 0)
        stop_text = f"{pit_stops} STOP" if pit_stops == 1 else f"{pit_stops} STOPS"
        self.lap_label.setText(f"{entry.lap_text} • L{laps_on_set} ({stop_text})")

        # In Pit Lane vs Track Racing status display
        in_pit = getattr(entry, "in_pit_lane", False)
        pit_state = getattr(entry, "pit_state", "RACING")

        if in_pit:
            self.sector_badge.setText("PIT")
            self.sector_badge.setStyleSheet(
                f"""
                background-color: rgba(255, 159, 28, 0.25);
                color: {THEME.AMBER};
                border: 1px solid {THEME.AMBER};
                border-radius: 3px;
                font-size: 10px;
                font-weight: 800;
                font-family: {FONT_FAMILY_MONO};
                """
            )

            if pit_state == "IN_BOX_STOP":
                self.gap_label.setText("BOX STOP")
                self.gap_label.setStyleSheet(
                    f"font-family: {FONT_FAMILY_MONO}; font-size: 11px; font-weight: 800; color: {THEME.RED};"
                )
                self.speed_label.setText("BOX 2.4s")
                self.speed_label.setStyleSheet(
                    f"font-family: {FONT_FAMILY_MONO}; font-size: 10px; font-weight: 700; color: {THEME.RED};"
                )
            else:
                self.gap_label.setText("PIT LANE")
                self.gap_label.setStyleSheet(
                    f"font-family: {FONT_FAMILY_MONO}; font-size: 11px; font-weight: 800; color: {THEME.AMBER};"
                )
                self.speed_label.setText(f"{entry.speed_kmh:4.1f} KM/H (LMT 80)")
                self.speed_label.setStyleSheet(
                    f"font-family: {FONT_FAMILY_MONO}; font-size: 10px; font-weight: 700; color: {THEME.AMBER};"
                )
        else:
            self.sector_badge.setText(f"S{entry.sector}")
            self.sector_badge.setStyleSheet(
                f"""
                background-color: {THEME.BG_BASE};
                color: {THEME.TEXT_SECONDARY};
                border: 1px solid {THEME.BORDER_MUTED};
                border-radius: 3px;
                font-size: 10px;
                font-weight: 700;
                font-family: {FONT_FAMILY_MONO};
                """
            )

            if entry.rank == 1:
                self.gap_label.setText("LEADER")
                self.gap_label.setStyleSheet(
                    f"font-family: {FONT_FAMILY_MONO}; font-size: 11px; font-weight: 700; color: {THEME.GREEN};"
                )
            else:
                self.gap_label.setText(entry.gap_text)
                self.gap_label.setStyleSheet(
                    f"font-family: {FONT_FAMILY_MONO}; font-size: 11px; font-weight: 700; color: {THEME.TEXT_SECONDARY};"
                )

            self.speed_label.setText(f"{entry.speed_kmh:5.1f} KM/H")
            self.speed_label.setStyleSheet(
                f"font-family: {FONT_FAMILY_MONO}; font-size: 10px; font-weight: 600; color: {THEME.TEXT_MUTED};"
            )

        # 2026 MOM Override Ready Indicator
        if getattr(entry, "override_ready", False):
            self.ovr_badge.show()
        else:
            self.ovr_badge.hide()

        # Visual styling based on selection
        if entry.is_selected:
            self.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {THEME.BG_SURFACE_ELEVATED};
                    border: 1px solid {entry.driver_color};
                    border-radius: 5px;
                }}
                """
            )
        else:
            self.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {THEME.BG_CARD};
                    border: 1px solid {THEME.BORDER_SUBTLE};
                    border-radius: 5px;
                }}
                QFrame:hover {{
                    background-color: {THEME.BG_SURFACE_HOVER};
                    border-color: {THEME.BORDER_MUTED};
                }}
                """
            )


class Leaderboard(QFrame):
    """Race order leaderboard panel."""

    driver_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("panelFrame")
        self.setMinimumWidth(280)
        self.setMaximumWidth(340)
        self.setStyleSheet(
            f"""
            QFrame#panelFrame {{
                background-color: {THEME.BG_SURFACE};
                border: 1px solid {THEME.BORDER_SUBTLE};
                border-radius: 6px;
            }}
            """
        )

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 8, 10, 8)
        self._layout.setSpacing(6)

        # Header
        header = QHBoxLayout()
        header.setContentsMargins(2, 0, 2, 0)
        title = QLabel("RACE LEADERBOARD")
        title.setStyleSheet(
            f"font-size: 11px; font-weight: 800; letter-spacing: 1.2px; color: {THEME.TEXT_SECONDARY};"
        )
        subtitle = QLabel("STANDINGS")
        subtitle.setStyleSheet(
            f"font-size: 10px; font-weight: 700; letter-spacing: 0.8px; color: {THEME.TEXT_MUTED};"
        )
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(subtitle)
        self._layout.addLayout(header)

        # Container for rows
        self._rows_container = QVBoxLayout()
        self._rows_container.setSpacing(6)
        self._layout.addLayout(self._rows_container)

        self._layout.addStretch(1)

        self._row_widgets: list[LeaderboardRowWidget] = []

    def update_standings(self, entries: list[LeaderboardEntry]) -> None:
        """Updates the leaderboard rows in-place or adjusts count."""
        # Ensure sufficient row widgets exist
        while len(self._row_widgets) < len(entries):
            row = LeaderboardRowWidget(self)
            row.clicked.connect(self.driver_selected.emit)
            self._rows_container.addWidget(row)
            self._row_widgets.append(row)

        # Hide extra rows if any
        for i in range(len(entries), len(self._row_widgets)):
            self._row_widgets[i].hide()

        # Update visible rows
        for i, entry in enumerate(entries):
            self._row_widgets[i].show()
            self._row_widgets[i].update_entry(entry)
