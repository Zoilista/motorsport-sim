"""Top Bar Widget for Motorsport Race Control Dashboard (Layout Scuderia).

Features:
- Fixed 48px height with pixel-perfect vertical alignment.
- Rebalanced 3-part layout preventing header text truncation.
- Integrated circuit selector, lap counter, flag badge, clock, and setup workbench trigger.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from ui.theme import FONT_FAMILY_MONO, THEME


class TopBar(QFrame):
    """Header bar displaying session identification, lap counter, and status."""

    setup_requested = Signal()
    circuit_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("topBar")
        self.setFixedHeight(48)
        self.setStyleSheet(
            f"""
            QFrame#topBar {{
                background-color: {THEME.BG_SURFACE};
                border-bottom: 1px solid {THEME.BORDER_SUBTLE};
            }}
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(16)

        # -------------------------------------------------------------
        # 1. LEFT SECTION: Logo / Title + Live Status Badge
        # -------------------------------------------------------------
        left_layout = QHBoxLayout()
        left_layout.setSpacing(10)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        title_label = QLabel("MOTORSPORT TELEMETRY")
        title_label.setObjectName("headerTitle")
        title_label.setStyleSheet(
            f"font-size: 13px; font-weight: 800; letter-spacing: 1.4px; color: {THEME.TEXT_PRIMARY};"
        )

        self.live_badge = QLabel("● LIVE")
        self.live_badge.setObjectName("liveBadge")
        self.live_badge.setStyleSheet(
            f"""
            background-color: rgba(0, 230, 118, 0.12);
            color: {THEME.GREEN};
            border: 1px solid rgba(0, 230, 118, 0.35);
            border-radius: 4px;
            padding: 2px 7px;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.8px;
            """
        )

        left_layout.addWidget(title_label)
        left_layout.addWidget(self.live_badge)

        # -------------------------------------------------------------
        # 2. CENTER SECTION: Circuit Selector + Lap Counter + Flag
        # -------------------------------------------------------------
        center_layout = QHBoxLayout()
        center_layout.setSpacing(12)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Circuit Selector dropdown
        self.combo_circuit = QComboBox()
        self.combo_circuit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.combo_circuit.addItems([
            "Prototype Circuit (5,200 m)",
            "Autodromo Nazionale Monza (5,793 m)",
            "Intercity Istanbul Park (5,338 m)",
            "Silverstone Circuit (5,891 m)",
        ])
        self.combo_circuit.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {THEME.BG_BASE};
                border: 1px solid {THEME.BORDER_MUTED};
                border-radius: 4px;
                color: {THEME.TEXT_PRIMARY};
                font-family: {FONT_FAMILY_MONO};
                font-size: 11px;
                font-weight: 700;
                padding: 3px 10px;
                min-width: 240px;
            }}
            QComboBox:hover {{
                border-color: {THEME.CYAN};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 18px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {THEME.BG_SURFACE_ELEVATED};
                border: 1px solid {THEME.BORDER_MUTED};
                color: {THEME.TEXT_PRIMARY};
                selection-background-color: rgba(0, 229, 255, 0.25);
                selection-color: {THEME.CYAN};
                padding: 4px;
            }}
            """
        )
        self.combo_circuit.currentTextChanged.connect(self.circuit_selected.emit)

        # Lap box
        lap_box = QFrame()
        lap_box.setStyleSheet(
            f"background-color: {THEME.BG_BASE}; border: 1px solid {THEME.BORDER_SUBTLE}; border-radius: 4px;"
        )
        lap_box_layout = QHBoxLayout(lap_box)
        lap_box_layout.setContentsMargins(8, 2, 8, 2)
        lap_box_layout.setSpacing(6)

        lap_prefix = QLabel("LAP")
        lap_prefix.setStyleSheet(
            f"font-size: 9px; font-weight: 800; color: {THEME.TEXT_MUTED}; letter-spacing: 0.8px;"
        )
        self.lap_value = QLabel("01 / 10")
        self.lap_value.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 12px; font-weight: 700; color: {THEME.TEXT_PRIMARY};"
        )
        lap_box_layout.addWidget(lap_prefix)
        lap_box_layout.addWidget(self.lap_value)

        # Race Flag badge
        self.flag_status = QLabel("GREEN FLAG")
        self.flag_status.setObjectName("flagBadge")
        self.flag_status.setStyleSheet(
            f"""
            background-color: rgba(0, 230, 118, 0.14);
            color: {THEME.GREEN};
            border: 1px solid rgba(0, 230, 118, 0.4);
            border-radius: 4px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.8px;
            """
        )

        center_layout.addWidget(self.combo_circuit)
        center_layout.addWidget(lap_box)
        center_layout.addWidget(self.flag_status)

        # -------------------------------------------------------------
        # 3. RIGHT SECTION: Simulation Clock + Workbench Button
        # -------------------------------------------------------------
        right_layout = QHBoxLayout()
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        time_box = QFrame()
        time_box.setStyleSheet(
            f"background-color: {THEME.BG_BASE}; border: 1px solid {THEME.BORDER_SUBTLE}; border-radius: 4px;"
        )
        time_box_layout = QHBoxLayout(time_box)
        time_box_layout.setContentsMargins(8, 2, 8, 2)
        time_box_layout.setSpacing(6)

        time_prefix = QLabel("SIM TIME")
        time_prefix.setStyleSheet(
            f"font-size: 9px; font-weight: 800; color: {THEME.TEXT_MUTED}; letter-spacing: 0.8px;"
        )
        self.elapsed_label = QLabel("00:00:00.0")
        self.elapsed_label.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 12px; font-weight: 700; color: {THEME.CYAN};"
        )
        time_box_layout.addWidget(time_prefix)
        time_box_layout.addWidget(self.elapsed_label)

        self.sim_indicator = QLabel("● ACTIVE")
        self.sim_indicator.setStyleSheet(
            f"color: {THEME.GREEN}; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;"
        )

        self.btn_workbench = QPushButton("⏸ SETUP WORKBENCH")
        self.btn_workbench.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_workbench.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {THEME.BG_SURFACE_ELEVATED};
                border: 1px solid {THEME.CYAN};
                border-radius: 4px;
                color: {THEME.CYAN};
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 0.8px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 229, 255, 0.15);
            }}
            """
        )
        self.btn_workbench.clicked.connect(self.setup_requested.emit)

        right_layout.addWidget(time_box)
        right_layout.addWidget(self.sim_indicator)
        right_layout.addWidget(self.btn_workbench)

        layout.addLayout(left_layout)
        layout.addStretch(1)
        layout.addLayout(center_layout)
        layout.addStretch(1)
        layout.addLayout(right_layout)

    def update_state(
        self,
        current_lap: int,
        total_laps: int,
        elapsed_seconds: float,
        is_finished: bool,
        is_paused: bool = False,
    ):
        """Updates the header elements."""
        self.lap_value.setText(f"{current_lap:02d} / {total_laps:02d}")

        # Format elapsed time as HH:MM:SS.d
        hours = int(elapsed_seconds // 3600)
        minutes = int((elapsed_seconds % 3600) // 60)
        seconds = int(elapsed_seconds % 60)
        millis = int((elapsed_seconds % 1.0) * 10)
        self.elapsed_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:1d}")

        if is_finished:
            self.flag_status.setText("CHECKERED FLAG")
            self.flag_status.setStyleSheet(
                """
                background-color: rgba(255, 255, 255, 0.15);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 4px;
                padding: 3px 10px;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.8px;
                """
            )
            self.sim_indicator.setText("■ FINISHED")
            self.sim_indicator.setStyleSheet(
                f"color: {THEME.TEXT_MUTED}; font-size: 10px; font-weight: 700;"
            )
            self.live_badge.setText("● FINISHED")
            self.live_badge.setStyleSheet(
                f"""
                background-color: rgba(255, 255, 255, 0.08);
                color: {THEME.TEXT_SECONDARY};
                border: 1px solid {THEME.BORDER_MUTED};
                border-radius: 4px;
                padding: 2px 7px;
                font-size: 10px;
                font-weight: 700;
                """
            )
            self.btn_workbench.setEnabled(False)
        elif is_paused:
            self.sim_indicator.setText("⏸ PAUSED")
            self.sim_indicator.setStyleSheet(
                f"color: {THEME.AMBER}; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;"
            )
            self.live_badge.setText("⏸ PAUSED")
            self.live_badge.setStyleSheet(
                f"""
                background-color: rgba(255, 159, 28, 0.15);
                color: {THEME.AMBER};
                border: 1px solid rgba(255, 159, 28, 0.45);
                border-radius: 4px;
                padding: 2px 7px;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.8px;
                """
            )
            self.btn_workbench.setText("▶ RESUME")
            self.btn_workbench.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {THEME.GREEN};
                    border: 1px solid {THEME.GREEN};
                    border-radius: 4px;
                    color: #051008;
                    padding: 4px 14px;
                    font-size: 11px;
                    font-weight: 800;
                    letter-spacing: 0.8px;
                }}
                QPushButton:hover {{
                    background-color: #00FF88;
                }}
                """
            )
        else:
            self.sim_indicator.setText("● ACTIVE")
            self.sim_indicator.setStyleSheet(
                f"color: {THEME.GREEN}; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;"
            )
            self.live_badge.setText("● LIVE")
            self.live_badge.setStyleSheet(
                f"""
                background-color: rgba(0, 230, 118, 0.12);
                color: {THEME.GREEN};
                border: 1px solid rgba(0, 230, 118, 0.35);
                border-radius: 4px;
                padding: 2px 7px;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.8px;
                """
            )
            self.btn_workbench.setText("⏸ SETUP WORKBENCH")
            self.btn_workbench.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {THEME.BG_SURFACE_ELEVATED};
                    border: 1px solid {THEME.CYAN};
                    border-radius: 4px;
                    color: {THEME.CYAN};
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: 800;
                    letter-spacing: 0.8px;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 229, 255, 0.15);
                }}
                """
            )
