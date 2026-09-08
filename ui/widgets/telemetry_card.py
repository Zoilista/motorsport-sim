"""Modular Telemetry Metric Card for Motorsport Sim (Layout Scuderia).

Features:
- Compact card architecture tailored for the 90px bottom telemetry strip.
- High-contrast typography with monospace value readouts and responsive unit alignments.
- Optional integrated mini gauge bar with dedicated accent colors.
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


class TelemetryCard(QFrame):
    """Reusable metric card displaying a single telemetry parameter."""

    def __init__(
        self,
        label: str,
        initial_value: str = "--",
        unit: str = "",
        show_bar: bool = False,
        bar_color: str = THEME.CYAN,
        accent_value_color: str | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("elevatedCard")
        self._bar_color = bar_color
        self._accent_color = accent_value_color or THEME.TEXT_PRIMARY

        self.setStyleSheet(
            f"""
            QFrame#elevatedCard {{
                background-color: {THEME.BG_CARD};
                border: 1px solid {THEME.BORDER_SUBTLE};
                border-radius: 5px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(2)

        # Header: Metric Title
        self.label_widget = QLabel(label.upper())
        self.label_widget.setStyleSheet(
            f"""
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 1px;
            color: {THEME.TEXT_SECONDARY};
            """
        )
        layout.addWidget(self.label_widget)

        # Center: Value and Unit
        val_unit_layout = QHBoxLayout()
        val_unit_layout.setContentsMargins(0, 0, 0, 0)
        val_unit_layout.setSpacing(4)
        val_unit_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBaseline)

        self.value_widget = QLabel(initial_value)
        self.value_widget.setStyleSheet(
            f"""
            font-family: {FONT_FAMILY_MONO};
            font-size: 20px;
            font-weight: 800;
            color: {self._accent_color};
            """
        )

        self.unit_widget = QLabel(unit.upper())
        self.unit_widget.setStyleSheet(
            f"""
            font-size: 9px;
            font-weight: 700;
            color: {THEME.TEXT_MUTED};
            letter-spacing: 0.6px;
            margin-bottom: 2px;
            """
        )

        val_unit_layout.addWidget(self.value_widget)
        if unit:
            val_unit_layout.addWidget(self.unit_widget)
        val_unit_layout.addStretch(1)

        layout.addLayout(val_unit_layout)

        # Optional Mini Gauge / Progress Bar
        self.progress_bar: QProgressBar | None = None
        if show_bar:
            pb = QProgressBar()
            pb.setRange(0, 100)
            pb.setValue(0)
            pb.setTextVisible(False)
            pb.setFixedHeight(3)
            pb.setStyleSheet(
                f"""
                QProgressBar {{
                    background-color: {THEME.BORDER_SUBTLE};
                    border: none;
                    border-radius: 1px;
                }}
                QProgressBar::chunk {{
                    background-color: {self._bar_color};
                    border-radius: 1px;
                }}
                """
            )
            layout.addWidget(pb)
            self.progress_bar = pb
        else:
            layout.addSpacing(3)

    def set_value(
        self,
        value_str: str,
        unit_str: str | None = None,
        ratio: float | None = None,
        override_color: str | None = None,
    ) -> None:
        """Update the displayed value, unit, and optional gauge."""
        self.value_widget.setText(value_str)
        if unit_str is not None:
            self.unit_widget.setText(unit_str.upper())

        color_to_use = override_color or self._accent_color
        self.value_widget.setStyleSheet(
            f"""
            font-family: {FONT_FAMILY_MONO};
            font-size: 20px;
            font-weight: 800;
            color: {color_to_use};
            """
        )

        if self.progress_bar is not None and ratio is not None:
            clamped = max(0, min(100, int(ratio * 100)))
            self.progress_bar.setValue(clamped)
