"""Script to refine and verify authentic F1 waypoint geometries for Monza, Istanbul Park, and Silverstone."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QApplication

from simulation.track import Track
from ui.theme import THEME
from ui.widgets.track_view import CarMarkerData, TrackCircuitCanvas

# ==============================================================================
# 1. AUTODROMO NAZIONALE MONZA (Clockwise)
# Official F1 layout:
# - Rettifilo straight on the left running upwards (South to North)
# - Variante del Rettifilo (T1-T2) sharp right-left chicane at top-left
# - Curva Grande (Biassono) sweeping fast right arc
# - Variante della Roggia (T4-T5) left-right chicane
# - Lesmo 1 & Lesmo 2 two sharp 90-degree right turns at top-right
# - Curva del Serraglio kinked straight heading down
# - Variante Ascari (T8-T9-T10) fast left-right-left chicane
# - Rettifilo delle Rogge (Back Straight) heading down to Parabolica
# - Curva Parabolica (Alboreto) huge sweeping 180-degree right curve at bottom
# ==============================================================================
MONZA_WAYPOINTS = [
    # Start / Finish Straight (Rettifilo, running South to North)
    (0.24, 0.72),  # S/F Line
    (0.24, 0.58),  # Rettifilo Straight mid
    (0.24, 0.44),  # DRS Zone
    (0.24, 0.32),  # Heavy braking 100m board
    (0.24, 0.22),  # T1 braking / entry
    # Variante del Rettifilo (T1-T2 sharp chicane)
    (0.22, 0.17),  # T1 right flick apex
    (0.25, 0.15),  # T2 left flick apex
    (0.28, 0.17),  # Rettifilo chicane exit
    # Curva Biassono (Curva Grande) - sweeping fast right
    (0.35, 0.20),  # Curva Grande entry
    (0.42, 0.22),  # Curva Grande mid
    (0.48, 0.21),  # Curva Grande exit
    # Approach to Variante della Roggia
    (0.53, 0.19),  # Roggia braking zone
    # Variante della Roggia (T4-T5 chicane)
    (0.56, 0.16),  # T4 left flick apex
    (0.59, 0.18),  # T5 right flick apex
    (0.62, 0.22),  # Roggia exit
    # Lesmo 1 & Lesmo 2
    (0.66, 0.25),  # Lesmo 1 approach
    (0.72, 0.26),  # Lesmo 1 (T6) 90-deg right apex
    (0.75, 0.24),  # Chute between Lesmos
    (0.78, 0.20),  # Lesmo 2 (T7) right apex
    (0.81, 0.22),  # Lesmo 2 exit
    # Curva del Serraglio (slight left kink heading down)
    (0.82, 0.28),  # Serraglio entry (under old oval banking)
    (0.81, 0.36),  # Serraglio mid
    (0.80, 0.44),  # Serraglio straight full throttle
    # Variante Ascari (T8-T9-T10 fast chicane)
    (0.79, 0.50),  # Ascari entry braking
    (0.76, 0.54),  # T8 fast left apex
    (0.78, 0.58),  # T9 fast right apex
    (0.75, 0.62),  # T10 left exit onto back straight
    # Back Straight (Rettifilo delle Rogge)
    (0.75, 0.68),  # Back Straight full throttle
    (0.75, 0.76),  # DRS Zone approaching Parabolica
    (0.75, 0.82),  # Parabolica heavy braking marker
    # Curva Parabolica (Curva Alboreto) - huge 180-degree right turn
    (0.74, 0.86),  # Parabolica entry
    (0.68, 0.88),  # Parabolica mid-corner long radius
    (0.56, 0.88),  # Parabolica opening exit
    (0.42, 0.87),  # Parabolica acceleration zone
    (0.32, 0.84),  # Unwinding onto pit straight
    (0.26, 0.80),  # Return to Rettifilo Straight
]


# ==============================================================================
# 2. INTERCITY ISTANBUL PARK (Anti-Clockwise)
# Official F1 layout:
# - Pit straight at bottom, heading right to left
# - Turn 1 downhill sharp left at bottom-left
# - Turn 2 uphill right sweeper
# - Turns 3-4-5 climbing left-right-left complex
# - Turn 6 sharp 90-degree right crest
# - Turn 7 blind right crest
# - Turn 8: Legendary 4-Apex left turn sweeping across top
# - Turn 9-10 downhill chicane
# - Back Straight (1.2 km) straight line heading down-right
# - Turn 12-13-14 final technical chicane
# - Turn 15 right onto pit straight
# ==============================================================================
ISTANBUL_WAYPOINTS = [
    # Start / Finish Straight (heading Right to Left along bottom)
    (0.60, 0.84),  # S/F Line
    (0.48, 0.84),  # Main straight full throttle
    (0.36, 0.84),  # DRS Zone
    (0.26, 0.84),  # Heavy braking 100m board
    (0.20, 0.83),  # Turn 1 crest
    # Turn 1 Downhill Left & Turn 2
    (0.15, 0.78),  # Turn 1 downhill apex
    (0.13, 0.70),  # Turn 1 exit dip
    (0.14, 0.62),  # Turn 2 uphill right sweeper
    # Turns 3-4-5 Climbing Complex
    (0.18, 0.54),  # Turn 3 left
    (0.22, 0.48),  # Turn 4 right kink
    (0.27, 0.42),  # Turn 5 left crest
    # Turn 6 & 7 Crests
    (0.33, 0.38),  # Turn 6 braking
    (0.36, 0.32),  # Turn 6 sharp 90-deg right apex
    (0.41, 0.30),  # Chute to Turn 7
    (0.46, 0.27),  # Turn 7 blind crest right apex
    (0.51, 0.25),  # Descent towards Turn 8
    # EFSANEVİ TURN 8 (Quad-Apex High-Speed Sweeper)
    (0.56, 0.22),  # Turn 8 Entry
    (0.62, 0.18),  # Turn 8 Apex 1 (left)
    (0.70, 0.16),  # Turn 8 Apex 2 (crest / peak lateral G)
    (0.78, 0.17),  # Turn 8 Apex 3 (left sweep)
    (0.85, 0.21),  # Turn 8 Apex 4 (exit apex)
    (0.89, 0.28),  # Turn 8 exit runoff
    # Turn 9-10 Chicane
    (0.88, 0.36),  # Turn 9 braking
    (0.85, 0.42),  # Turn 9 left apex
    (0.82, 0.47),  # Turn 10 right apex
    # Long Back Straight (1.2 km) heading down-left towards chicane
    (0.80, 0.54),  # Back straight acceleration
    (0.76, 0.63),  # Back straight mid (DRS / X-Mode)
    (0.73, 0.71),  # Back straight full throttle
    (0.70, 0.78),  # Back straight heavy braking
    # Turn 12-13-14 Final Chicane (left-right-left)
    (0.68, 0.82),  # Turn 12 left entry
    (0.66, 0.86),  # Turn 13 right curb
    (0.68, 0.89),  # Turn 14 left curb
    # Turn 15 onto Start/Finish Straight
    (0.71, 0.87),  # Turn 15 right sweeper
    (0.69, 0.84),  # Pit straight entry
]


# ==============================================================================
# 3. SILVERSTONE CIRCUIT (Clockwise)
# Official modern F1 Arena layout:
# - Hamilton Straight on left/center running up-right
# - Abbey (T1) fast right, Farm Curve (T2) left
# - Arena complex: Village (T3) sharp right, The Loop (T4) tight hairpin left,
#   Aintree (T5) left onto Wellington Straight
# - Wellington Straight heading towards Brooklands
# - Brooklands (T6) left, Luffield (T7) long right carousel, Woodcote (T8) right
# - Copse (T9) high-speed right
# - Maggotts - Becketts - Chapel (T10-T14) high-speed Esses sequence
# - Hangar Straight heading down-right
# - Stowe (T15) fast right
# - Vale (T16) slow left chicane, Club (T17-18) double-apex right onto Hamilton Straight
# ==============================================================================
SILVERSTONE_WAYPOINTS = [
    # Hamilton Straight (Start / Finish Line)
    (0.38, 0.78),  # S/F Line
    (0.44, 0.74),  # Hamilton Straight
    (0.50, 0.70),  # Abbey Approach
    # Turn 1 (Abbey) & Turn 2 (Farm Curve)
    (0.55, 0.67),  # Turn 1 (Abbey) fast right apex
    (0.58, 0.63),  # Farm Curve (left kink)
    # Arena Complex: Village & The Loop & Aintree
    (0.59, 0.57),  # Approach to Village
    (0.57, 0.52),  # Turn 3 (Village) sharp right apex
    (0.52, 0.50),  # The Loop entry braking
    (0.47, 0.52),  # Turn 4 (The Loop) tight hairpin left apex
    (0.48, 0.56),  # The Loop exit
    (0.51, 0.60),  # Turn 5 (Aintree) left curve
    # Wellington Straight (heading West-North-West towards Brooklands)
    (0.46, 0.62),  # Wellington Straight entry
    (0.38, 0.63),  # Wellington Straight mid (DRS Zone)
    (0.30, 0.64),  # Wellington Straight braking
    # Brooklands & Luffield & Woodcote
    (0.24, 0.63),  # Turn 6 (Brooklands) left entry
    (0.20, 0.60),  # Brooklands apex
    (0.18, 0.54),  # Turn 7 (Luffield) carousel entry
    (0.17, 0.48),  # Luffield mid carousel
    (0.20, 0.44),  # Turn 8 (Woodcote) right exit
    (0.25, 0.43),  # Old National Pit Straight
    # Turn 9 (Copse) High-Speed Right
    (0.32, 0.41),  # Copse braking zone
    (0.38, 0.38),  # Turn 9 (Copse) ultra-fast right apex
    (0.44, 0.35),  # Copse exit
    # Maggotts - Becketts - Chapel Complex (High-Speed S-curves)
    (0.48, 0.31),  # Turn 10 (Maggotts) fast left entry
    (0.52, 0.27),  # Turn 11 (Becketts 1) high-speed right flick
    (0.56, 0.26),  # Turn 12 (Becketts 2) sharp right apex
    (0.60, 0.28),  # Turn 13 (Chapel) left exit curve
    # Hangar Straight (heading South-East)
    (0.66, 0.34),  # Hangar Straight entry
    (0.72, 0.42),  # Hangar Straight mid (full throttle / DRS)
    (0.78, 0.50),  # Hangar Straight approach to Stowe
    (0.83, 0.58),  # Stowe braking marker
    # Turn 15 (Stowe) Fast Right
    (0.85, 0.64),  # Turn 15 (Stowe) fast right apex
    (0.83, 0.70),  # Stowe exit chute towards Vale
    (0.78, 0.74),  # Approach to Vale
    # Turn 16 (Vale) & Turn 17-18 (Club)
    (0.72, 0.76),  # Turn 16 (Vale) sharp left chicane
    (0.66, 0.77),  # Turn 17 (Club 1) right entry
    (0.58, 0.79),  # Turn 18 (Club 2) final right apex
    (0.48, 0.80),  # Club exit onto Hamilton Straight
]


def render_and_save():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    out_dir = os.path.join(os.path.dirname(__file__), "circuit_renders")
    os.makedirs(out_dir, exist_ok=True)

    circuits = [
        ("Monza", MONZA_WAYPOINTS, "monza_circuit.png"),
        ("Istanbul Park", ISTANBUL_WAYPOINTS, "istanbul_park_circuit.png"),
        ("Silverstone", SILVERSTONE_WAYPOINTS, "silverstone_circuit.png"),
    ]

    for name, wps, filename in circuits:
        canvas = TrackCircuitCanvas()
        canvas.resize(QSize(960, 640))
        track = Track(name=name, length=5500.0, sector_lengths=(1800.0, 1900.0, 1800.0), waypoints=wps)
        canvas.set_track(track)

        sample_cars = [
            CarMarkerData("VER", 1, 0.04, "#3671C6", is_selected=False),
            CarMarkerData("HAM", 44, 0.25, "#6CD3BF", is_selected=False),
            CarMarkerData("LEC", 16, 0.52, "#F91536", is_selected=True),
            CarMarkerData("NOR", 4, 0.74, "#FF8000", is_selected=False),
            CarMarkerData("ALO", 14, 0.90, "#229971", is_selected=False),
        ]
        canvas.set_cars(sample_cars)

        pixmap = QPixmap(QSize(960, 640))
        pixmap.fill(QColor(THEME.BG_CARD))
        canvas.render(pixmap)

        filepath = os.path.join(out_dir, filename)
        pixmap.save(filepath, "PNG")
        print(f"Rendered {name}: {len(wps)} waypoints -> {filepath}")


if __name__ == "__main__":
    render_and_save()
