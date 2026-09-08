"""Bottom Status Bar for Motorsport Sim."""

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QWidget,
)

from ui.theme import FONT_FAMILY_MONO, THEME


class BottomBar(QFrame):
    """Footer bar displaying telemetry stream health, tick rate, and circuit metadata."""

    def __init__(
        self,
        circuit_name: str = "Prototype Circuit",
        circuit_length_m: float = 5200.0,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("bottomBar")
        self.setFixedHeight(30)
        self.setStyleSheet(
            f"""
            QFrame#bottomBar {{
                background-color: {THEME.BG_DARKEST};
                border-top: 1px solid {THEME.BORDER_SUBTLE};
            }}
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(20)

        # 1. Circuit metadata
        self.circuit_label = QLabel(
            f"CIRCUIT: {circuit_name.upper()}  |  {circuit_length_m:,.0f} M  |  3 SECTORS"
        )
        self.circuit_label.setStyleSheet(
            f"font-size: 10px; font-weight: 700; color: {THEME.TEXT_MUTED}; letter-spacing: 0.8px;"
        )

        # 2. Engine specs
        self.engine_label = QLabel("ENGINE: 20 HZ (50 MS)  |  PHYSICS: ACTIVE")
        self.engine_label.setStyleSheet(
            f"font-family: {FONT_FAMILY_MONO}; font-size: 10px; font-weight: 600; color: {THEME.TEXT_MUTED};"
        )

        # 3. Connection status
        self.status_label = QLabel("● TELEMETRY STREAM ONLINE")
        self.status_label.setStyleSheet(
            f"font-size: 10px; font-weight: 800; color: {THEME.GREEN}; letter-spacing: 0.8px;"
        )

        layout.addWidget(self.circuit_label)
        layout.addStretch(1)
        layout.addWidget(self.engine_label)
        layout.addStretch(1)
        layout.addWidget(self.status_label)

    def update_circuit(self, circuit_name: str, circuit_length_m: float):
        """Updates circuit metadata in the bottom status bar."""
        self.circuit_label.setText(
            f"CIRCUIT: {circuit_name.upper()}  |  {circuit_length_m:,.0f} M  |  3 SECTORS"
        )

    def set_finished_status(self):
        self.status_label.setText("■ SESSION COMPLETED")
        self.status_label.setStyleSheet(
            f"font-size: 10px; font-weight: 800; color: {THEME.TEXT_SECONDARY}; letter-spacing: 0.8px;"
        )
