"""Visual verification script rendering all authentic circuit geometries to high-res PNG images.

Outputs rendered pixmaps to scratch/circuit_renders/:
- monza_circuit.png
- istanbul_park_circuit.png
- silverstone_circuit.png
- prototype_circuit.png
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure UTF-8 output encoding for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication

from simulation.track_library import TrackLibrary
from ui.theme import THEME
from ui.widgets.track_view import CarMarkerData, TrackCircuitCanvas


def render_circuit_to_image(track, output_path: str, canvas_size: QSize = QSize(960, 640)) -> dict:
    """Renders a Track instance using TrackCircuitCanvas to a high-res PNG."""
    canvas = TrackCircuitCanvas()
    canvas.resize(canvas_size)
    canvas.set_track(track)

    # Add sample cars to demonstrate car markers and telemetry highlights
    sample_cars = [
        CarMarkerData("VER", 1, 0.05, "#3671C6", is_selected=False),
        CarMarkerData("HAM", 44, 0.22, "#6CD3BF", is_selected=False),
        CarMarkerData("LEC", 16, 0.48, "#F91536", is_selected=True),  # Highlighted driver
        CarMarkerData("NOR", 4, 0.73, "#FF8000", is_selected=False),
        CarMarkerData("ALO", 14, 0.88, "#229971", is_selected=False),
    ]
    canvas.set_cars(sample_cars)

    # Render offscreen onto QPixmap
    pixmap = QPixmap(canvas_size)
    pixmap.fill(QColor(THEME.BG_CARD))
    canvas.render(pixmap)

    # Save PNG
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    saved = pixmap.save(output_path, "PNG")

    # Compute geometric diagnostic metrics
    span_x = canvas._max_x - canvas._min_x
    span_y = canvas._max_y - canvas._min_y
    aspect_ratio = span_x / max(1e-5, span_y)

    return {
        "name": track.name,
        "length_m": track.length,
        "waypoints_count": len(track.waypoints),
        "spline_points": len(canvas._track_points),
        "bounds_x": (round(canvas._min_x, 3), round(canvas._max_x, 3)),
        "bounds_y": (round(canvas._min_y, 3), round(canvas._max_y, 3)),
        "aspect_ratio": round(aspect_ratio, 2),
        "saved": saved,
        "path": os.path.abspath(output_path),
    }


def main():
    # Headless-safe Qt App initialization
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    out_dir = os.path.join(os.path.dirname(__file__), "circuit_renders")
    os.makedirs(out_dir, exist_ok=True)

    tracks = [
        ("Monza", TrackLibrary.get_monza(), "monza_circuit.png"),
        ("Istanbul Park", TrackLibrary.get_istanbul_park(), "istanbul_park_circuit.png"),
        ("Silverstone", TrackLibrary.get_silverstone(), "silverstone_circuit.png"),
        ("Prototype", TrackLibrary.get_prototype(), "prototype_circuit.png"),
    ]

    print("=" * 70)
    print("MOTORSPORT SIMULATION // AUTHENTIC CIRCUIT GEOMETRY RENDERS")
    print("=" * 70)

    for label, track, filename in tracks:
        path = os.path.join(out_dir, filename)
        meta = render_circuit_to_image(track, path)
        print(f"\n[CIRCUIT] {meta['name']}")
        print(f"  Physical Length : {meta['length_m']:,.0f} m")
        print(f"  Waypoints       : {meta['waypoints_count']} points")
        print(f"  Spline Vertices : {meta['spline_points']} points")
        print(f"  Normalized X    : [{meta['bounds_x'][0]:.3f}, {meta['bounds_x'][1]:.3f}]")
        print(f"  Normalized Y    : [{meta['bounds_y'][0]:.3f}, {meta['bounds_y'][1]:.3f}]")
        print(f"  Aspect Ratio    : {meta['aspect_ratio']:.2f}")
        print(f"  Render Saved    : {meta['saved']} -> {meta['path']}")

    print("\n" + "=" * 70)
    print("ALL CIRCUIT RENDERS GENERATED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
