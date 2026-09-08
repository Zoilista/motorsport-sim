"""Track Library of Real-World Motorsport Circuits.

Provides authentic segment specifications, sector demarcations, and 2D normalized
spline waypoints for:
- Autodromo Nazionale Monza (Italy)
- Intercity Istanbul Park (Turkey)
- Silverstone Circuit (United Kingdom)
- Prototype Circuit (Standard GP)
"""


from simulation.track import Track, TrackSegment


class TrackLibrary:
    """Factory and registry for real-world racing circuits."""

    @staticmethod
    def get_monza() -> Track:
        """Autodromo Nazionale Monza (5,793 m) — The Temple of Speed."""
        segments = [
            # --- SECTOR 1 (1,900 m) ---
            TrackSegment("Rettifilo Straight", "straight", 1120.0, None, sector=1, direction="straight"),
            TrackSegment("Variante del Rettifilo (T1-T2)", "corner", 150.0, radius=35.0, sector=1, direction="right"),
            TrackSegment("Curva Biassono (Curva Grande)", "corner", 630.0, radius=380.0, sector=1, direction="right"),

            # --- SECTOR 2 (1,950 m) ---
            TrackSegment("Variante della Roggia Straight", "straight", 280.0, None, sector=2, direction="straight"),
            TrackSegment("Variante della Roggia (T4-T5)", "corner", 160.0, radius=55.0, sector=2, direction="left"),
            TrackSegment("Lesmo 1 Approach", "straight", 180.0, None, sector=2, direction="straight"),
            TrackSegment("Prima Variante Lesmo (T6)", "corner", 140.0, radius=85.0, sector=2, direction="right"),
            TrackSegment("Lesmo Intermediate Link", "straight", 130.0, None, sector=2, direction="straight"),
            TrackSegment("Seconda Variante Lesmo (T7)", "corner", 160.0, radius=75.0, sector=2, direction="right"),
            TrackSegment("Curva del Serraglio Straight", "straight", 900.0, None, sector=2, direction="straight"),

            # --- SECTOR 3 (1,943 m) ---
            TrackSegment("Variante Ascari (T8-T9-T10)", "corner", 290.0, radius=70.0, sector=3, direction="left"),
            TrackSegment("Parabolica Approach Straight", "straight", 953.0, None, sector=3, direction="straight"),
            TrackSegment("Curva Parabolica (Curva Alboreto)", "corner", 700.0, radius=140.0, sector=3, direction="right"),
        ]

        # Authentic real-world satellite GPS waypoints (36 waypoints)
        waypoints = [
            (0.126, 0.610), (0.134, 0.550), (0.143, 0.490), (0.152, 0.430),
            (0.175, 0.378), (0.169, 0.324), (0.175, 0.264), (0.208, 0.208),
            (0.287, 0.170), (0.385, 0.154), (0.488, 0.149), (0.590, 0.145),
            (0.676, 0.124), (0.773, 0.106), (0.871, 0.100), (0.895, 0.157),
            (0.900, 0.216), (0.811, 0.246), (0.721, 0.276), (0.638, 0.310),
            (0.560, 0.350), (0.484, 0.390), (0.406, 0.430), (0.360, 0.478),
            (0.313, 0.529), (0.301, 0.588), (0.290, 0.648), (0.280, 0.708),
            (0.269, 0.768), (0.258, 0.828), (0.246, 0.888), (0.159, 0.900),
            (0.105, 0.850), (0.100, 0.790), (0.103, 0.730), (0.114, 0.670),
        ]

        return Track(
            name="Autodromo Nazionale Monza",
            length=5793.0,
            sector_lengths=(1900.0, 1950.0, 1943.0),
            segments=segments,
            mu=1.75,
            waypoints=waypoints,
        )

    @staticmethod
    def get_istanbul_park() -> Track:
        """Intercity Istanbul Park (5,338 m) — Anti-Clockwise Rollercoaster."""
        segments = [
            # --- SECTOR 1 (1,600 m) ---
            TrackSegment("Main Straight", "straight", 650.0, None, sector=1, direction="straight"),
            TrackSegment("Turn 1 Downhill", "corner", 160.0, radius=60.0, sector=1, direction="left"),
            TrackSegment("T1-T2 Chute", "straight", 190.0, None, sector=1, direction="straight"),
            TrackSegment("Turn 2 Sweeper", "corner", 140.0, radius=75.0, sector=1, direction="right"),
            TrackSegment("Turn 3-4-5 Uphill Complex", "corner", 460.0, radius=130.0, sector=1, direction="left"),

            # --- SECTOR 2 (1,950 m) ---
            TrackSegment("Approach to Turn 6", "straight", 210.0, None, sector=2, direction="straight"),
            TrackSegment("Turn 6 Sharp Right", "corner", 130.0, radius=65.0, sector=2, direction="right"),
            TrackSegment("T6-T7 Chute", "straight", 160.0, None, sector=2, direction="straight"),
            TrackSegment("Turn 7 Blind Crest", "corner", 150.0, radius=70.0, sector=2, direction="right"),
            TrackSegment("Approach to Turn 8", "straight", 220.0, None, sector=2, direction="straight"),
            # Efsanevi 4-Apeksli Turn 8: Devasa yanal G ve sağ lastiklere (FR & RR) aşırı termal yük!
            TrackSegment("Turn 8 Quad-Apex Sweeper", "corner", 680.0, radius=180.0, sector=2, direction="left"),
            TrackSegment("Turn 9-10 Chicane", "corner", 400.0, radius=110.0, sector=2, direction="right"),

            # --- SECTOR 3 (1,788 m) ---
            TrackSegment("Long Back Straight", "straight", 1188.0, None, sector=3, direction="straight"),
            TrackSegment("Turn 12-13-14 Final Chicane", "corner", 280.0, radius=42.0, sector=3, direction="left"),
            TrackSegment("Pit Straight Entry Curve", "corner", 320.0, radius=160.0, sector=3, direction="right"),
        ]

        # Authentic real-world satellite GPS waypoints (36 waypoints)
        waypoints = [
            (0.365, 0.850), (0.447, 0.830), (0.505, 0.788), (0.499, 0.697),
            (0.560, 0.636), (0.639, 0.607), (0.722, 0.599), (0.786, 0.561),
            (0.806, 0.491), (0.869, 0.464), (0.820, 0.398), (0.745, 0.356),
            (0.671, 0.314), (0.632, 0.251), (0.711, 0.240), (0.793, 0.259),
            (0.871, 0.252), (0.900, 0.173), (0.849, 0.100), (0.768, 0.106),
            (0.688, 0.132), (0.608, 0.159), (0.528, 0.187), (0.530, 0.269),
            (0.504, 0.357), (0.479, 0.446), (0.453, 0.534), (0.395, 0.597),
            (0.321, 0.641), (0.247, 0.685), (0.174, 0.730), (0.100, 0.774),
            (0.104, 0.824), (0.119, 0.900), (0.201, 0.886), (0.283, 0.868),
        ]

        return Track(
            name="Intercity Istanbul Park",
            length=5338.0,
            sector_lengths=(1600.0, 1950.0, 1788.0),
            segments=segments,
            mu=1.75,
            waypoints=waypoints,
        )

    @staticmethod
    def get_silverstone() -> Track:
        """Silverstone Circuit (5,891 m) — The Home of British Motor Racing."""
        segments = [
            # --- SECTOR 1 (1,850 m) ---
            TrackSegment("Hamilton Straight", "straight", 520.0, None, sector=1, direction="straight"),
            TrackSegment("Abbey Curve (Turn 1)", "corner", 180.0, radius=220.0, sector=1, direction="right"),
            TrackSegment("Farm Curve (Turn 2)", "corner", 160.0, radius=300.0, sector=1, direction="left"),
            TrackSegment("Village Hairpin (Turn 3)", "corner", 140.0, radius=45.0, sector=1, direction="right"),
            TrackSegment("The Loop (Turn 4)", "corner", 150.0, radius=38.0, sector=1, direction="left"),
            TrackSegment("Aintree Curve (Turn 5)", "corner", 140.0, radius=180.0, sector=1, direction="left"),
            TrackSegment("Wellington Straight", "straight", 560.0, None, sector=1, direction="straight"),

            # --- SECTOR 2 (2,050 m) ---
            TrackSegment("Brooklands (Turn 6)", "corner", 200.0, radius=110.0, sector=2, direction="left"),
            TrackSegment("Luffield (Turn 7)", "corner", 280.0, radius=75.0, sector=2, direction="right"),
            TrackSegment("Woodcote (Turn 8)", "corner", 220.0, radius=320.0, sector=2, direction="right"),
            TrackSegment("National Pit Straight", "straight", 350.0, None, sector=2, direction="straight"),
            TrackSegment("Copse (Turn 9, High-Speed)", "corner", 220.0, radius=240.0, sector=2, direction="right"),
            TrackSegment("Maggotts (Turn 10)", "corner", 210.0, radius=260.0, sector=2, direction="left"),
            TrackSegment("Becketts (Turn 11-12)", "corner", 250.0, radius=140.0, sector=2, direction="right"),
            TrackSegment("Chapel (Turn 13)", "corner", 220.0, radius=280.0, sector=2, direction="left"),
            TrackSegment("Hangar Straight Entry", "straight", 100.0, None, sector=2, direction="straight"),

            # --- SECTOR 3 (1,991 m) ---
            TrackSegment("Hangar Straight", "straight", 880.0, None, sector=3, direction="straight"),
            TrackSegment("Stowe (Turn 15)", "corner", 230.0, radius=130.0, sector=3, direction="right"),
            TrackSegment("Vale Chicane (Turn 16)", "corner", 180.0, radius=50.0, sector=3, direction="left"),
            TrackSegment("Club Corner (Turn 17-18)", "corner", 360.0, radius=120.0, sector=3, direction="right"),
            TrackSegment("Pit Straight Approach", "straight", 341.0, None, sector=3, direction="straight"),
        ]

        # Authentic real-world satellite GPS waypoints (38 waypoints, modern Hamilton Straight S/F)
        waypoints = [
            (0.247, 0.578), (0.323, 0.520), (0.431, 0.500), (0.551, 0.497),
            (0.649, 0.452), (0.727, 0.467), (0.790, 0.463), (0.780, 0.395),
            (0.689, 0.346), (0.597, 0.297), (0.506, 0.248), (0.414, 0.199),
            (0.329, 0.224), (0.256, 0.258), (0.275, 0.192), (0.348, 0.135),
            (0.463, 0.113), (0.586, 0.106), (0.709, 0.100), (0.815, 0.125),
            (0.849, 0.194), (0.863, 0.267), (0.869, 0.340), (0.898, 0.407),
            (0.884, 0.477), (0.900, 0.541), (0.806, 0.586), (0.747, 0.650),
            (0.688, 0.714), (0.629, 0.778), (0.568, 0.841), (0.496, 0.900),
            (0.392, 0.882), (0.328, 0.820), (0.246, 0.765), (0.149, 0.759),
            (0.100, 0.695), (0.172, 0.636),
        ]

        return Track(
            name="Silverstone Circuit",
            length=5891.0,
            sector_lengths=(1850.0, 2050.0, 1991.0),
            segments=segments,
            mu=1.75,
            waypoints=waypoints,
        )

    @staticmethod
    def get_prototype() -> Track:
        """Prototype Circuit (5,200 m) — Standard GP test venue."""
        track = Track(
            name="Prototype Circuit",
            length=5200.0,
            sector_lengths=(1700.0, 1800.0, 1700.0),
        )
        # Default layout waypoints (27 waypoints)
        track.waypoints = [
            (0.20, 0.82),  # Start/Finish Line
            (0.35, 0.82),  # Pit Straight
            (0.50, 0.82),  # Pit Straight Mid
            (0.65, 0.82),  # DRS Zone
            (0.78, 0.80),  # T1 Braking
            (0.86, 0.75),  # Turn 1 Hairpin Apex
            (0.88, 0.65),  # Turn 2 Sweeper
            (0.84, 0.54),  # Curva Grande Transition
            (0.74, 0.46),  # Esses Left
            (0.76, 0.36),  # Esses Right
            (0.82, 0.26),  # Infield Hairpin Approach
            (0.84, 0.18),  # Infield Hairpin Entry
            (0.78, 0.14),  # Hairpin Apex
            (0.70, 0.15),  # Hairpin Exit
            (0.58, 0.20),  # Back Straight
            (0.45, 0.22),  # Back Straight Mid
            (0.32, 0.22),  # Back Straight DRS
            (0.22, 0.19),  # Chicane Approach
            (0.16, 0.26),  # Chicane Left
            (0.18, 0.35),  # Chicane Right
            (0.24, 0.42),  # Infield Chute
            (0.30, 0.50),  # Infield Apex
            (0.28, 0.60),  # Infield Exit
            (0.20, 0.68),  # Final Sector Curve
            (0.14, 0.72),  # Final Turn Apex
            (0.14, 0.79),  # Final Turn Exit
            (0.16, 0.82),  # Straight Entry
        ]
        return track

    @classmethod
    def get_track(cls, name_or_key: str) -> Track:
        """Retrieves track instance by name, abbreviation or keyword."""
        key = name_or_key.lower()
        if "monza" in key:
            return cls.get_monza()
        elif "istanbul" in key or "turkey" in key:
            return cls.get_istanbul_park()
        elif "silverstone" in key or "britain" in key:
            return cls.get_silverstone()
        else:
            return cls.get_prototype()

    @classmethod
    def get_available_tracks(cls) -> list[str]:
        return [
            "Prototype Circuit (5,200 m)",
            "Autodromo Nazionale Monza (5,793 m)",
            "Intercity Istanbul Park (5,338 m)",
            "Silverstone Circuit (5,891 m)",
        ]
