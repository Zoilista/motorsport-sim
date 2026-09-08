"""Tests dynamic switching between all 4 circuits in MainWindow."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import QApplication

from simulation.race import Race
from simulation.track_library import TrackLibrary
from ui.main_window import MainWindow


def test_circuit_switching():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    track = TrackLibrary.get_prototype()
    race = Race(track=track, laps=5)
    window = MainWindow(race)

    circuits = [
        "Autodromo Nazionale Monza",
        "Intercity Istanbul Park",
        "Silverstone Circuit",
        "Prototype Circuit",
    ]

    for circuit in circuits:
        print(f"Switching to: {circuit}...")
        window.on_circuit_selected(circuit)
        assert window.view_model.track_name.lower() in circuit.lower(), f"Name mismatch for {circuit}"
        assert len(window.track_view.canvas._track_points) > 500, f"Spline not generated for {circuit}"
        print(f"  -> SUCCESS: Spline vertices={len(window.track_view.canvas._track_points)}, S1={window.track_view.canvas._sector_fractions[0]:.3f}, S2={window.track_view.canvas._sector_fractions[1]:.3f}")

    print("\nALL CIRCUITS SWITCHED CLEANLY IN UI!")


if __name__ == "__main__":
    test_circuit_switching()
