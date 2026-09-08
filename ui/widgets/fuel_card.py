"""Fuel & Energy Status Card (Backwards-Compatibility Adapter for EnergyCard)."""

from PySide6.QtWidgets import QWidget

from ui.widgets.energy_card import EnergyCard


class FuelCard(EnergyCard):
    """Backwards-compatible wrapper subclassing EnergyCard."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
