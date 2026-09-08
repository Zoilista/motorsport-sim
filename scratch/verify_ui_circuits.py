"""Visual UI verification of dynamic track switching, TrackView layouts, and TyreCard."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication

from simulation.race import Race
from simulation.track_library import TrackLibrary
from ui.main_window import MainWindow
from ui.widgets.track_view import TrackView
from ui.widgets.tyre_card import TyreCard


def verify_ui():
    app = QApplication.instance() or QApplication(sys.argv)

    artifact_dir = Path("C:/Users/GORKEM/.gemini/antigravity-ide/brain/7f4dc4fc-7ecb-44aa-bd44-70d64b8dfbcb")

    print("[1] Rendering track layouts for all circuits...")
    track_view = TrackView("Prototype Circuit")
    track_view.resize(500, 360)

    circuits = [
        ("prototype", "layout_prototype.png"),
        ("monza", "layout_monza.png"),
        ("istanbul", "layout_istanbul.png"),
        ("silverstone", "layout_silverstone.png"),
    ]

    for key, filename in circuits:
        trk = TrackLibrary.get_track(key)
        track_view.set_track(trk)
        pixmap = QPixmap(track_view.size())
        pixmap.fill(Qt.GlobalColor.black)
        track_view.render(pixmap)
        pixmap.save(str(artifact_dir / filename))
        print(f" -> Rendered {trk.name} -> {filename}")

    print("[2] Verifying MainWindow circuit switching...")
    initial_track = TrackLibrary.get_prototype()
    race = Race(track=initial_track, laps=10)
    window = MainWindow(race)
    window.resize(1440, 900)
    window.show()

    # Switch to Istanbul Park
    window.on_circuit_selected("Intercity Istanbul Park (5,338 m)")
    assert window.view_model.track_name == "Intercity Istanbul Park", "Track name mismatch!"
    assert window.view_model.track_length == 5338.0, "Track length mismatch!"
    print(" -> Switched to Intercity Istanbul Park successfully!")

    # Step simulation 20 ticks (1 sec)
    for _ in range(20):
        window.update_simulation()

    # Capture main window
    win_pix = QPixmap(window.size())
    window.render(win_pix)
    win_pix.save(str(artifact_dir / "dashboard_istanbul_park.png"))
    print(f" -> Rendered live dashboard to dashboard_istanbul_park.png")

    print(">>> ALL VISUAL VERIFICATIONS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    verify_ui()
