"""Motorsport Sim - Engineering Dark Theme & Design Tokens.

Provides centralized styling, color tokens, and QSS rules for pit-wall race engineering UI.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeColors:
    # Backgrounds
    BG_DARKEST: str = "#06080C"
    BG_BASE: str = "#0A0E17"
    BG_SURFACE: str = "#111722"
    BG_SURFACE_ELEVATED: str = "#161E2E"
    BG_SURFACE_HOVER: str = "#1D283C"
    BG_CARD: str = "#0E141F"

    # Borders & Dividers
    BORDER_SUBTLE: str = "#1C2433"
    BORDER_MUTED: str = "#2B374D"
    BORDER_ACCENT: str = "#00E5FF"

    # Text
    TEXT_PRIMARY: str = "#F3F6FB"
    TEXT_SECONDARY: str = "#95A5BE"
    TEXT_MUTED: str = "#586985"
    TEXT_INVERSE: str = "#06080C"

    # Telemetry & Status Accents
    CYAN: str = "#00E5FF"
    AMBER: str = "#FF9F1C"
    GREEN: str = "#00E676"
    RED: str = "#FF3366"
    PURPLE: str = "#B388FF"
    YELLOW: str = "#FFD600"

    # Driver Specific Brandings
    DRIVER_A: str = "#00E5FF"  # Cyan
    DRIVER_B: str = "#FF9F1C"  # Amber


THEME = ThemeColors()

FONT_FAMILY_SANS = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', 'Roboto', sans-serif"
)
FONT_FAMILY_MONO = (
    "'Consolas', 'SF Mono', 'Roboto Mono', 'Cascadia Code', monospace"
)


def get_application_stylesheet() -> str:
    """Returns the master QSS stylesheet for the application."""
    return f"""
    QMainWindow {{
        background-color: {THEME.BG_BASE};
    }}

    QWidget {{
        color: {THEME.TEXT_PRIMARY};
        font-family: {FONT_FAMILY_SANS};
        font-size: 12px;
    }}

    /* Global Scrollbars */
    QScrollBar:vertical {{
        background: {THEME.BG_BASE};
        width: 6px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {THEME.BORDER_MUTED};
        min-height: 20px;
        border-radius: 3px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* Panels & Containers */
    QFrame#panelFrame {{
        background-color: {THEME.BG_SURFACE};
        border: 1px solid {THEME.BORDER_SUBTLE};
        border-radius: 6px;
    }}

    QFrame#elevatedCard {{
        background-color: {THEME.BG_CARD};
        border: 1px solid {THEME.BORDER_SUBTLE};
        border-radius: 5px;
    }}

    /* Labels */
    QLabel {{
        background-color: transparent;
    }}

    QLabel#headerTitle {{
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1.2px;
        color: {THEME.TEXT_PRIMARY};
    }}

    QLabel#sectionHeader {{
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.1px;
        color: {THEME.TEXT_SECONDARY};
        text-transform: uppercase;
    }}

    QLabel#metricValue {{
        font-family: {FONT_FAMILY_MONO};
        font-size: 24px;
        font-weight: 700;
        color: {THEME.TEXT_PRIMARY};
    }}

    QLabel#metricUnit {{
        font-size: 10px;
        font-weight: 700;
        color: {THEME.TEXT_MUTED};
        letter-spacing: 0.8px;
    }}

    QLabel#metricLabel {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.1px;
        color: {THEME.TEXT_SECONDARY};
    }}

    /* Badges & Pills */
    QLabel#liveBadge {{
        background-color: rgba(0, 230, 118, 0.12);
        color: {THEME.GREEN};
        border: 1px solid rgba(0, 230, 118, 0.35);
        border-radius: 4px;
        padding: 3px 8px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.8px;
    }}

    QLabel#flagBadge {{
        background-color: rgba(0, 230, 118, 0.14);
        color: {THEME.GREEN};
        border: 1px solid rgba(0, 230, 118, 0.4);
        border-radius: 4px;
        padding: 3px 10px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.8px;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {THEME.BG_SURFACE_ELEVATED};
        border: 1px solid {THEME.BORDER_SUBTLE};
        border-radius: 4px;
        color: {THEME.TEXT_PRIMARY};
        padding: 5px 12px;
        font-size: 11px;
        font-weight: 700;
    }}
    QPushButton:hover {{
        background-color: {THEME.BG_SURFACE_HOVER};
        border-color: {THEME.BORDER_MUTED};
    }}
    QPushButton:pressed {{
        background-color: {THEME.BG_BASE};
    }}
    """
