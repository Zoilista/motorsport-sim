"""Tests rolled Silverstone waypoints starting on Hamilton Straight."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QApplication

from simulation.track import Track
from ui.theme import THEME
from ui.widgets.track_view import CarMarkerData, TrackCircuitCanvas

SILVERSTONE_RAW = [
    (0.586, 0.106), (0.709, 0.1), (0.815, 0.125), (0.849, 0.194), (0.863, 0.267),
    (0.869, 0.34), (0.898, 0.407), (0.884, 0.477), (0.9, 0.541), (0.806, 0.586),
    (0.747, 0.65), (0.688, 0.714), (0.629, 0.778), (0.568, 0.841), (0.496, 0.9),
    (0.392, 0.882), (0.328, 0.82), (0.246, 0.765), (0.149, 0.759), (0.1, 0.695),
    (0.172, 0.636), (0.247, 0.578), (0.323, 0.52), (0.431, 0.5), (0.551, 0.497),
    (0.649, 0.452), (0.727, 0.467), (0.79, 0.463), (0.78, 0.395), (0.689, 0.346),
    (0.597, 0.297), (0.506, 0.248), (0.414, 0.199), (0.329, 0.224), (0.256, 0.258),
    (0.275, 0.192), (0.348, 0.135), (0.463, 0.113)
]

# Roll by 21 so waypoint 0 is on Hamilton Straight
SILVERSTONE_MODERN = SILVERSTONE_RAW[21:] + SILVERSTONE_RAW[:21]

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

canvas = TrackCircuitCanvas()
canvas.resize(QSize(960, 640))
track = Track(
    name="Silverstone Circuit",
    length=5891.0,
    sector_lengths=(1850.0, 2050.0, 1991.0),
    waypoints=SILVERSTONE_MODERN,
)
canvas.set_track(track)

sample_cars = [
    CarMarkerData("VER", 1, 0.05, "#3671C6", is_selected=False),
    CarMarkerData("HAM", 44, 0.25, "#6CD3BF", is_selected=False),
    CarMarkerData("LEC", 16, 0.50, "#F91536", is_selected=True),
    CarMarkerData("NOR", 4, 0.75, "#FF8000", is_selected=False),
    CarMarkerData("ALO", 14, 0.90, "#229971", is_selected=False),
]
canvas.set_cars(sample_cars)

pixmap = QPixmap(QSize(960, 640))
pixmap.fill(QColor(THEME.BG_CARD))
canvas.render(pixmap)

out_path = os.path.join(os.path.dirname(__file__), "circuit_renders", "silverstone_circuit.png")
pixmap.save(out_path, "PNG")
print(f"Rendered modern Silverstone to {out_path}")
