import json
import math
import os
import sys
import urllib.request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QApplication

from simulation.track import Track
from ui.theme import THEME
from ui.widgets.track_view import CarMarkerData, TrackCircuitCanvas


def fetch_geojson_coords(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    feature = data["features"][0]
    coords = feature["geometry"]["coordinates"]
    return coords


def geo_to_cartesian(coords):
    """Converts [lon, lat] list to flat Cartesian coordinates preserving local scale."""
    lats = [c[1] for c in coords]
    mid_lat = math.radians(sum(lats) / len(lats))
    cos_lat = math.cos(mid_lat)

    pts = []
    for lon, lat in coords:
        # Screen Y is inverted relative to North latitude
        x = lon * cos_lat
        y = -lat
        pts.append((x, y))
    return pts


def subsample_by_distance(pts, target_count: int = 36):
    """Subsamples points along cumulative path length evenly."""
    # Compute cumulative distances
    cum_dists = [0.0]
    for i in range(1, len(pts)):
        d = math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        cum_dists.append(cum_dists[-1] + d)

    total_len = cum_dists[-1]
    step = total_len / target_count

    subsampled = []
    for i in range(target_count):
        target_d = i * step
        # Find segment
        idx = 0
        while idx < len(cum_dists) - 1 and cum_dists[idx + 1] < target_d:
            idx += 1
        d0 = cum_dists[idx]
        d1 = cum_dists[idx + 1] if idx + 1 < len(cum_dists) else total_len
        frac = (target_d - d0) / max(1e-9, d1 - d0)
        p0 = pts[idx]
        p1 = pts[(idx + 1) % len(pts)]
        interp_x = p0[0] + frac * (p1[0] - p0[0])
        interp_y = p0[1] + frac * (p1[1] - p0[1])
        subsampled.append((interp_x, interp_y))

    return subsampled


def normalize_to_box(pts, pad=0.08):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    span_x = max(1e-6, max_x - min_x)
    span_y = max(1e-6, max_y - min_y)

    norm_pts = []
    for x, y in pts:
        nx = pad + (x - min_x) / span_x * (1.0 - 2.0 * pad)
        ny = pad + (y - min_y) / span_y * (1.0 - 2.0 * pad)
        norm_pts.append((round(nx, 3), round(ny, 3)))
    return norm_pts


def main():
    brain_dir = os.path.dirname(os.path.abspath(__file__))

    urls = [
        ("Monza", "https://raw.githubusercontent.com/bacinger/f1-circuits/master/circuits/it-1922.geojson", 36, "monza_circuit.png"),
        ("Istanbul Park", "https://raw.githubusercontent.com/bacinger/f1-circuits/master/circuits/tr-2005.geojson", 36, "istanbul_park_circuit.png"),
        ("Silverstone", "https://raw.githubusercontent.com/bacinger/f1-circuits/master/circuits/gb-1948.geojson", 38, "silverstone_circuit.png"),
    ]

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    out_dir = os.path.join(brain_dir, "circuit_renders")
    os.makedirs(out_dir, exist_ok=True)

    result_waypoints = {}

    for name, url, count, out_name in urls:
        raw_coords = fetch_geojson_coords(url)
        cartesian = geo_to_cartesian(raw_coords)
        subsampled = subsample_by_distance(cartesian, target_count=count)
        normalized = normalize_to_box(subsampled, pad=0.10)
        result_waypoints[name] = normalized

        print(f"\n// --- {name.upper()} ({len(normalized)} WAYPOINTS) ---")
        print(normalized)

        # Render and save image
        canvas = TrackCircuitCanvas()
        canvas.resize(QSize(960, 640))
        track = Track(name=name, length=5500.0, sector_lengths=(1800.0, 1900.0, 1800.0), waypoints=normalized)
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

        img_path = os.path.join(out_dir, out_name)
        pixmap.save(img_path, "PNG")
        print(f"Rendered to {img_path}")


if __name__ == "__main__":
    main()
