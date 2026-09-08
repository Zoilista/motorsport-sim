import sys

from PySide6.QtWidgets import QApplication

from simulation.race import Race
from simulation.track import Track
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    track = Track(
        name="Prototype Circuit",
        length=5200.0,
        sector_lengths=(
            1700.0,
            1800.0,
            1700.0,
        ),
    )

    race = Race(
        track=track,
        laps=10,
    )

    window = MainWindow(race)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
