"""Track and Segment Data Models for Motorsport Simulation."""

import math
from dataclasses import dataclass, field


@dataclass
class TrackSegment:
    """Individual segment of a racing circuit (straight or corner)."""

    name: str
    type: str  # "straight" or "corner"
    length: float  # meters
    radius: float | None = None  # meters (None for straight)
    sector: int = 1  # 1, 2, or 3
    start_pos: float = 0.0
    end_pos: float = 0.0
    apex_speed_ms: float = float("inf")
    direction: str = "straight"  # "left", "right", or "straight"


@dataclass
class Track:
    """Represents a racing circuit comprised of sequential geometric segments."""

    name: str
    length: float
    sector_lengths: tuple[float, float, float]
    segments: list[TrackSegment] = field(default_factory=list)
    mu: float = 1.75  # High-downforce F1 slick grip coefficient (1.6 - 1.8)
    g: float = 9.81  # Gravitational acceleration (m/s^2)
    waypoints: list[tuple[float, float]] = field(default_factory=list)

    def __post_init__(self):
        if not self.segments:
            self.segments = self._build_default_segments()
        if not self.waypoints:
            self.waypoints = [
                (0.20, 0.82), (0.35, 0.82), (0.50, 0.82), (0.65, 0.82),
                (0.78, 0.80), (0.86, 0.75), (0.88, 0.65), (0.84, 0.54),
                (0.74, 0.46), (0.76, 0.36), (0.82, 0.26), (0.84, 0.18),
                (0.78, 0.14), (0.70, 0.15), (0.58, 0.20), (0.45, 0.22),
                (0.32, 0.22), (0.22, 0.19), (0.16, 0.26), (0.18, 0.35),
                (0.24, 0.42), (0.30, 0.50), (0.28, 0.60), (0.20, 0.68),
                (0.14, 0.72), (0.14, 0.79), (0.16, 0.82),
            ]
        self._calculate_segment_bounds_and_speeds()

    def _build_default_segments(self) -> list[TrackSegment]:
        """Constructs realistic 15-segment Prototype Circuit summing to 5,200m."""
        return [
            # --- SECTOR 1 (1,700 m) ---
            TrackSegment("Main Straight", "straight", 720.0, None, sector=1, direction="straight"),
            TrackSegment("Turn 1 Hairpin", "corner", 140.0, radius=48.0, sector=1, direction="right"),
            TrackSegment("T1-T2 Chute", "straight", 180.0, None, sector=1, direction="straight"),
            TrackSegment("Turn 2 Chicane", "corner", 160.0, radius=80.0, sector=1, direction="left"),
            TrackSegment("Curva Grande", "corner", 500.0, radius=360.0, sector=1, direction="right"),

            # --- SECTOR 2 (1,800 m) ---
            TrackSegment("DRS Straight 2", "straight", 450.0, None, sector=2, direction="straight"),
            TrackSegment("Turn 4 Infield Hairpin", "corner", 150.0, radius=45.0, sector=2, direction="left"),
            TrackSegment("Intermediate Straight", "straight", 300.0, None, sector=2, direction="straight"),
            TrackSegment("Turn 5-6 Esses", "corner", 400.0, radius=220.0, sector=2, direction="right"),
            TrackSegment("Back Straight", "straight", 500.0, None, sector=2, direction="straight"),

            # --- SECTOR 3 (1,700 m) ---
            TrackSegment("Turn 7 High-Speed Sweeper", "corner", 320.0, radius=280.0, sector=3, direction="left"),
            TrackSegment("Stadium Straight", "straight", 380.0, None, sector=3, direction="straight"),
            TrackSegment("Turn 8 Double Apex", "corner", 240.0, radius=75.0, sector=3, direction="right"),
            TrackSegment("Parabolica Approach", "straight", 260.0, None, sector=3, direction="straight"),
            TrackSegment("Turn 9 Final Parabolica", "corner", 500.0, radius=250.0, sector=3, direction="right"),
        ]

    def _calculate_segment_bounds_and_speeds(self):
        """Calculates start/end positions and physical apex speed limits."""
        current_pos = 0.0
        for seg in self.segments:
            seg.start_pos = current_pos
            current_pos += seg.length
            seg.end_pos = current_pos

            if seg.type == "corner" and seg.radius is not None and seg.radius > 0:
                # v_max = sqrt(mu * g * R)
                seg.apex_speed_ms = math.sqrt(self.mu * self.g * seg.radius)
            else:
                seg.apex_speed_ms = float("inf")

    def get_sector(self, position: float) -> int:
        """Returns sector (1, 2, 3) for a given distance along the circuit."""
        s1, s2, _ = self.sector_lengths
        norm_pos = position % self.length

        if norm_pos < s1:
            return 1
        if norm_pos < s1 + s2:
            return 2
        return 3

    def get_segment(self, position: float) -> TrackSegment:
        """Finds the active track segment at the given track position."""
        norm_pos = position % self.length
        for seg in self.segments:
            if seg.start_pos <= norm_pos < seg.end_pos:
                return seg
        return self.segments[-1]

    def get_upcoming_corners(
        self, position: float, horizon_m: float = 400.0
    ) -> list[tuple[TrackSegment, float]]:
        """Returns upcoming corner segments and distances to their start within horizon_m.

        Handles track wraparound (crossing S/F line) seamlessly.
        """
        norm_pos = position % self.length
        upcoming = []

        for seg in self.segments:
            if seg.type != "corner":
                continue

            # Case 1: Car is inside the corner
            if seg.start_pos <= norm_pos < seg.end_pos:
                upcoming.append((seg, 0.0))
                continue

            # Case 2: Corner is ahead on current lap
            if seg.start_pos > norm_pos:
                dist = seg.start_pos - norm_pos
                if dist <= horizon_m:
                    upcoming.append((seg, dist))
                continue

            # Case 3: Corner is ahead across the S/F line (next lap)
            dist_wrap = (self.length - norm_pos) + seg.start_pos
            if dist_wrap <= horizon_m:
                upcoming.append((seg, dist_wrap))

        # Sort by closest distance first
        upcoming.sort(key=lambda item: item[1])
        return upcoming
