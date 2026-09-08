import math
from typing import List, Tuple

def catmull_rom(raw_waypoints: List[Tuple[float, float]], steps_per_segment: int = 25) -> List[Tuple[float, float]]:
    pts = []
    total = len(raw_waypoints)
    for i in range(total):
        p0 = raw_waypoints[(i - 1) % total]
        p1 = raw_waypoints[i]
        p2 = raw_waypoints[(i + 1) % total]
        p3 = raw_waypoints[(i + 2) % total]

        for s in range(steps_per_segment):
            t = s / steps_per_segment
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (
                (2 * p1[0])
                + (-p0[0] + p2[0]) * t
                + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                (2 * p1[1])
                + (-p0[1] + p2[1]) * t
                + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            pts.append((x, y))
    return pts

def check_track(name: str, wps: List[Tuple[float, float]]):
    print(f"Checking {name}: {len(wps)} waypoints...")
    for idx, (x, y) in enumerate(wps):
        assert 0.05 <= x <= 0.95, f"{name} wp {idx} x={x} out of [0.05, 0.95]"
        assert 0.05 <= y <= 0.95, f"{name} wp {idx} y={y} out of [0.05, 0.95]"

    spline = catmull_rom(wps)
    min_x = min(p[0] for p in spline)
    max_x = max(p[0] for p in spline)
    min_y = min(p[1] for p in spline)
    max_y = max(p[1] for p in spline)
    span_x = max_x - min_x
    span_y = max_y - min_y
    aspect = span_x / span_y
    print(f"  Spline points: {len(spline)}")
    print(f"  Bounds: X=[{min_x:.3f}, {max_x:.3f}], Y=[{min_y:.3f}, {max_y:.3f}]")
    print(f"  Span: dx={span_x:.3f}, dy={span_y:.3f}, aspect ratio (w/h)={aspect:.2f}")

if __name__ == "__main__":
    monza_wps = [
        (0.68, 0.86), (0.56, 0.86), (0.44, 0.86), (0.34, 0.86), (0.26, 0.86),
        (0.22, 0.83), (0.21, 0.79), (0.23, 0.74), (0.25, 0.65), (0.26, 0.55),
        (0.25, 0.44), (0.23, 0.36), (0.21, 0.31), (0.23, 0.27), (0.27, 0.25),
        (0.33, 0.23), (0.39, 0.21), (0.43, 0.17), (0.47, 0.17), (0.51, 0.18),
        (0.55, 0.16), (0.60, 0.18), (0.66, 0.23), (0.73, 0.30), (0.79, 0.38),
        (0.83, 0.44), (0.85, 0.48), (0.82, 0.53), (0.81, 0.60), (0.81, 0.69),
        (0.81, 0.77), (0.82, 0.82), (0.86, 0.85), (0.85, 0.86), (0.78, 0.86)
    ]
    check_track("Monza", monza_wps)

    istanbul_wps = [
        (0.56, 0.82), (0.46, 0.82), (0.36, 0.82), (0.26, 0.82), (0.20, 0.82),
        (0.15, 0.78), (0.12, 0.72), (0.12, 0.65), (0.15, 0.58), (0.18, 0.52),
        (0.23, 0.47), (0.29, 0.44), (0.35, 0.41), (0.38, 0.35), (0.42, 0.33),
        (0.47, 0.30), (0.52, 0.27), (0.58, 0.24), (0.65, 0.20), (0.73, 0.17),
        (0.81, 0.18), (0.87, 0.23), (0.90, 0.31), (0.88, 0.39), (0.85, 0.46),
        (0.81, 0.51), (0.78, 0.58), (0.74, 0.66), (0.70, 0.74), (0.66, 0.81),
        (0.63, 0.86), (0.60, 0.89), (0.62, 0.92), (0.65, 0.88), (0.63, 0.82)
    ]
    check_track("Istanbul Park", istanbul_wps)

    silverstone_wps = [
        (0.24, 0.72), (0.29, 0.72), (0.34, 0.72), (0.39, 0.69), (0.42, 0.63),
        (0.43, 0.56), (0.40, 0.50), (0.35, 0.47), (0.30, 0.49), (0.31, 0.54),
        (0.35, 0.58), (0.42, 0.57), (0.50, 0.55), (0.58, 0.54), (0.64, 0.57),
        (0.67, 0.62), (0.69, 0.67), (0.71, 0.73), (0.69, 0.79), (0.64, 0.82),
        (0.67, 0.77), (0.72, 0.71), (0.77, 0.65), (0.82, 0.58), (0.85, 0.50),
        (0.84, 0.43), (0.80, 0.38), (0.75, 0.36), (0.68, 0.34), (0.58, 0.31),
        (0.48, 0.28), (0.40, 0.26), (0.34, 0.28), (0.30, 0.35), (0.26, 0.44),
        (0.24, 0.52), (0.22, 0.59), (0.21, 0.66), (0.22, 0.70)
    ]
    check_track("Silverstone", silverstone_wps)
