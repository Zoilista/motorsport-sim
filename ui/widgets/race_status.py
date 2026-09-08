"""Selected Driver Race Status & Timing Panel (Layout Scuderia).

Features:
- High-contrast, non-overlapping typography with explicit line-heights and padding.
- Crisp situational stats: LAP, GAP TO LEADER, CURRENT SECTOR, TOTAL DISTANCE.
- Precision timing matrix: CURRENT, LAST, BEST, and SEC 1 / SEC 2 / SEC 3 breakdown.
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


def format_lap_time(seconds: float | None) -> str:
    """Formats time as MM:SS.mmm or returns placeholder."""
    if seconds is None or seconds <= 0:
        return "--:--.---"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1.0) * 1000)
    return f"{mins:02d}:{secs:02d}.{millis:03d}"


def format_sector_time(seconds: float | None) -> str:
    """Formats sector time as SS.mmm or returns placeholder."""
    if seconds is None or seconds <= 0:
        return "--.---"
    secs = int(seconds)
    millis = int((seconds % 1.0) * 1000)
    return f"{secs:02d}.{millis:03d}"


class RaceStatusPanel(QFrame):
    """Right-side panel displaying selected driver's race situation and timing matrix."""

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
        # 1. Header: Driver Info & Position
        # -------------------------------------------------------------
        header_frame = QFrame()
        header_frame.setStyleSheet(
            f"background-color: {THEME.BG_CARD}; border: 1px solid {THEME.BORDER_SUBTLE}; border-radius: 4px;"
        )
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 5, 8, 5)
        header_layout.setSpacing(8)

        self.num_badge = QLabel("#07")
        self.num_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.num_badge.setFixedSize(34, 24)
        self.num_badge.setStyleSheet(
            f"""
            background-color: rgba(0, 229, 255, 0.15);
            color: {THEME.CYAN};
            border: 1px solid rgba(0, 229, 255, 0.5);
            border-radius: 3px;
            font-family: {FONT_FAMILY_MONO};
            font-size: 12px;
            font-weight: 800;
            """
        )

        name_layout = QVBoxLayout()
        name_layout.setSpacing(1)
        self.driver_name = QLabel("DRIVER A")
        self.driver_name.setStyleSheet(
            f"font-size: 13px; font-weight: 800; color: {THEME.TEXT_PRIMARY}; letter-spacing: 0.8px;"
        )
        self.driver_role = QLabel("PRIMARY TELEMETRY FOCUS")
        self.driver_role.setStyleSheet(
            f"font-size: 8px; font-weight: 700; color: {THEME.TEXT_MUTED}; letter-spacing: 0.8px;"
        )
        name_layout.addWidget(self.driver_name)
        name_layout.addWidget(self.driver_role)

        self.rank_badge = QLabel("P1")
        self.rank_badge.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 18px; font-weight: 800; color: {THEME.GREEN};"
        )

        header_layout.addWidget(self.num_badge)
        header_layout.addLayout(name_layout)
        header_layout.addStretch(1)
        header_layout.addWidget(self.rank_badge)

        layout.addWidget(header_frame)

        # -------------------------------------------------------------
        # 2. Key Situational Stats Grid
        # -------------------------------------------------------------
        stats_box = QFrame()
        stats_box.setStyleSheet(
            f"background-color: {THEME.BG_CARD}; border: 1px solid {THEME.BORDER_SUBTLE}; border-radius: 4px;"
        )
        stats_grid = QGridLayout(stats_box)
        stats_grid.setContentsMargins(8, 6, 8, 6)
        stats_grid.setHorizontalSpacing(10)
        stats_grid.setVerticalSpacing(4)

        def create_stat(label: str, initial: str):
            lbl = QLabel(label.upper())
            lbl.setStyleSheet(f"font-size: 8px; font-weight: 800; color: {THEME.TEXT_MUTED}; letter-spacing: 0.8px;")
            val = QLabel(initial)
            val.setStyleSheet(f"font-family: {FONT_FAMILY_MONO}; font-size: 11px; font-weight: 700; color: {THEME.TEXT_PRIMARY};")
            return lbl, val

        lbl_lap, self.val_lap = create_stat("LAP", "01 / 10")
        lbl_gap, self.val_gap = create_stat("GAP TO LEADER", "LEADER")
        lbl_sec, self.val_sec = create_stat("CURRENT SECTOR", "SECTOR 1")
        lbl_dist, self.val_dist = create_stat("TOTAL DISTANCE", "0.0 M")

        stats_grid.addWidget(lbl_lap, 0, 0)
        stats_grid.addWidget(self.val_lap, 1, 0)
        stats_grid.addWidget(lbl_gap, 0, 1)
        stats_grid.addWidget(self.val_gap, 1, 1)

        stats_grid.addWidget(lbl_sec, 2, 0)
        stats_grid.addWidget(self.val_sec, 3, 0)
        stats_grid.addWidget(lbl_dist, 2, 1)
        stats_grid.addWidget(self.val_dist, 3, 1)

        layout.addWidget(stats_box)

        # -------------------------------------------------------------
        # 3. Timing Matrix (Lap & Sectors)
        # -------------------------------------------------------------
        timing_frame = QFrame()
        timing_frame.setStyleSheet(
            f"background-color: {THEME.BG_CARD}; border: 1px solid {THEME.BORDER_SUBTLE}; border-radius: 4px;"
        )
        timing_layout = QVBoxLayout(timing_frame)
        timing_layout.setContentsMargins(8, 6, 8, 6)
        timing_layout.setSpacing(6)

        timing_title = QLabel("LAP & SECTOR TIMING (MEASURED)")
        timing_title.setStyleSheet(
            f"font-size: 9px; font-weight: 800; color: {THEME.TEXT_SECONDARY}; letter-spacing: 1.1px;"
        )
        timing_layout.addWidget(timing_title)

        timing_grid = QGridLayout()
        timing_grid.setHorizontalSpacing(10)
        timing_grid.setVerticalSpacing(3)

        lbl_cur, self.val_cur_lap = create_stat("CURRENT LAP", "--:--.---")
        lbl_last, self.val_last_lap = create_stat("LAST LAP", "--:--.---")
        lbl_best, self.val_best_lap = create_stat("BEST LAP", "--:--.---")

        timing_grid.addWidget(lbl_cur, 0, 0)
        timing_grid.addWidget(self.val_cur_lap, 0, 1)
        timing_grid.addWidget(lbl_last, 1, 0)
        timing_grid.addWidget(self.val_last_lap, 1, 1)
        timing_grid.addWidget(lbl_best, 2, 0)
        timing_grid.addWidget(self.val_best_lap, 2, 1)

        timing_layout.addLayout(timing_grid)

        # Sector breakdown row
        sec_layout = QHBoxLayout()
        sec_layout.setSpacing(6)

        def create_sector_box(sec_name: str):
            box = QFrame()
            box.setStyleSheet(
                f"background-color: {THEME.BG_BASE}; border: 1px solid {THEME.BORDER_SUBTLE}; border-radius: 3px;"
            )
            v = QVBoxLayout(box)
            v.setContentsMargins(4, 2, 4, 2)
            v.setSpacing(1)
            lbl = QLabel(sec_name)
            lbl.setStyleSheet(f"font-size: 8px; font-weight: 800; color: {THEME.TEXT_MUTED};")
            t = QLabel("--.---")
            t.setStyleSheet(f"font-family: {FONT_FAMILY_MONO}; font-size: 10px; font-weight: 700; color: {THEME.TEXT_PRIMARY};")
            v.addWidget(lbl)
            v.addWidget(t)
            return box, t

        box_s1, self.val_s1 = create_sector_box("SEC 1")
        box_s2, self.val_s2 = create_sector_box("SEC 2")
        box_s3, self.val_s3 = create_sector_box("SEC 3")

        sec_layout.addWidget(box_s1)
        sec_layout.addWidget(box_s2)
        sec_layout.addWidget(box_s3)

        timing_layout.addLayout(sec_layout)
        layout.addWidget(timing_frame)

    def update_status(self, snapshot: DriverSnapshot | None) -> None:
        """Updates all driver summary telemetry values."""
        if snapshot is None:
            return

        self.num_badge.setText(f"#{snapshot.number:02d}")
        self.num_badge.setStyleSheet(
            f"""
            background-color: {snapshot.color}22;
            color: {snapshot.color};
            border: 1px solid {snapshot.color}77;
            border-radius: 3px;
            font-family: {FONT_FAMILY_MONO};
            font-size: 12px;
            font-weight: 800;
            """
        )
        self.driver_name.setText(snapshot.name.upper())
        self.rank_badge.setText(f"P{snapshot.position_rank}")

        self.val_lap.setText(f"{snapshot.current_lap:02d} / {snapshot.total_laps:02d}")
        if snapshot.position_rank == 1:
            self.val_gap.setText("LEADER")
            self.val_gap.setStyleSheet(
                f"font-family: {FONT_FAMILY_MONO}; font-size: 11px; font-weight: 700; color: {THEME.GREEN};"
            )
        else:
            self.val_gap.setText(f"+{snapshot.gap_to_leader_s:.3f}s")
            self.val_gap.setStyleSheet(
                f"font-family: {FONT_FAMILY_MONO}; font-size: 11px; font-weight: 700; color: {THEME.TEXT_PRIMARY};"
            )

        self.val_sec.setText(f"SECTOR {snapshot.sector}")
        self.val_dist.setText(f"{snapshot.total_distance:,.0f} M")

        # Lap timings
        self.val_cur_lap.setText(format_lap_time(snapshot.current_lap_time_s))
        self.val_last_lap.setText(format_lap_time(snapshot.last_lap_time_s))
        self.val_best_lap.setText(format_lap_time(snapshot.best_lap_time_s))

        # Sector timings
        s1_time = snapshot.sector_times_s.get(1)
        s2_time = snapshot.sector_times_s.get(2)
        s3_time = snapshot.sector_times_s.get(3)

        self.val_s1.setText(format_sector_time(s1_time))
        self.val_s2.setText(format_sector_time(s2_time))
        self.val_s3.setText(format_sector_time(s3_time))
