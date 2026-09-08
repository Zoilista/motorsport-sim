"""Inspects waypoint indices to align Start/Finish line to modern Grand Prix S/F positions."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scratch.extract_real_waypoints import (
    fetch_geojson_coords,
    geo_to_cartesian,
    normalize_to_box,
    subsample_by_distance,
)

# Fetch Silverstone
raw_silverstone = fetch_geojson_coords("https://raw.githubusercontent.com/bacinger/f1-circuits/master/circuits/gb-1948.geojson")
silverstone_cart = geo_to_cartesian(raw_silverstone)
silverstone_sub = subsample_by_distance(silverstone_cart, target_count=38)
silverstone_norm = normalize_to_box(silverstone_sub, pad=0.10)

print("SILVERSTONE WAYPOINTS:")
for idx, pt in enumerate(silverstone_norm):
    print(f"  {idx:2d}: {pt}")

# Fetch Monza
raw_monza = fetch_geojson_coords("https://raw.githubusercontent.com/bacinger/f1-circuits/master/circuits/it-1922.geojson")
monza_cart = geo_to_cartesian(raw_monza)
monza_sub = subsample_by_distance(monza_cart, target_count=36)
monza_norm = normalize_to_box(monza_sub, pad=0.10)

print("\nMONZA WAYPOINTS:")
for idx, pt in enumerate(monza_norm):
    print(f"  {idx:2d}: {pt}")

# Fetch Istanbul
raw_istanbul = fetch_geojson_coords("https://raw.githubusercontent.com/bacinger/f1-circuits/master/circuits/tr-2005.geojson")
istanbul_cart = geo_to_cartesian(raw_istanbul)
istanbul_sub = subsample_by_distance(istanbul_cart, target_count=36)
istanbul_norm = normalize_to_box(istanbul_sub, pad=0.10)

print("\nISTANBUL WAYPOINTS:")
for idx, pt in enumerate(istanbul_norm):
    print(f"  {idx:2d}: {pt}")
