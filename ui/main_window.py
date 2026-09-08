"""Main Window for Motorsport Telemetry Dashboard (Layout Scuderia).

Implements the modern 3-column engineering dashboard architecture:
1. TopBar (48px): Session branding, circuit selector, lap counter, flag badge, clock, and workbench button.
2. Main Content (3 Columns):
   - Left Column (~300px): Live Leaderboard with hover/active selection.
   - Middle Column (Flexible): Authentic Track View (upper) + Full-width Speed Waveform (lower).
   - Right Column (~360px): Selected Driver Status, 4-Wheel Tyre Monitor, and Powertrain/ERS Card.
3. Bottom Strip (86px): Compact 6-metric telemetry strip (SPEED, GEAR, RPM, THROTTLE, BRAKE, AERO MODE).
"""


from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from simulation.race import Race
from simulation.track_library import TrackLibrary
from ui.theme import THEME, get_application_stylesheet
from ui.view_models.race_view_model import RaceViewModel
from ui.widgets.energy_card import EnergyCard
from ui.widgets.leaderboard import Leaderboard
from ui.widgets.race_status import RaceStatusPanel
from ui.widgets.setup_workbench_dialog import SetupWorkbenchDialog
from ui.widgets.telemetry_graph import TelemetryGraph
from ui.widgets.telemetry_panel import TelemetryPanel
from ui.widgets.top_bar import TopBar
from ui.widgets.track_view import CarMarkerData, TrackView
from ui.widgets.tyre_card import TyreCard


class MainWindow(QMainWindow):
    """Main window hosting the motorsport pit-wall telemetry dashboard."""

    def __init__(self, race: Race):
        super().__init__()
        self.setWindowTitle("Motorsport Simulation // Pit-Wall Telemetry & Race Control")
        self.setMinimumSize(1280, 720)
        self.resize(1440, 900)

        self.is_paused: bool = False

        # Ensure main window accepts strong focus for keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Initialize View-Model layer
        self.view_model = RaceViewModel(race)

        # Apply global application stylesheet
        self.setStyleSheet(get_application_stylesheet())

        # Main layout structure
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # -------------------------------------------------------------
        # 1. Top Header Bar (48px)
        # -------------------------------------------------------------
        self.top_bar = TopBar(self)
        self.top_bar.setup_requested.connect(self.toggle_pause_workbench)
        self.top_bar.circuit_selected.connect(self.on_circuit_selected)
        root_layout.addWidget(self.top_bar)

        # Space Shortcut for Pause / Workbench Toggle
        self.space_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.space_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.space_shortcut.activated.connect(self.toggle_pause_workbench)

        # Content container
        content_container = QWidget()
        content_container.setStyleSheet(f"background-color: {THEME.BG_BASE};")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(10, 8, 10, 8)
        content_layout.setSpacing(8)

        # -------------------------------------------------------------
        # 2. Main Middle Section: 3-Column Layout Scuderia
        # -------------------------------------------------------------
        main_columns_layout = QHBoxLayout()
        main_columns_layout.setSpacing(8)

        # Left Column (~300px): Live Leaderboard
        self.leaderboard = Leaderboard(self)
        self.leaderboard.driver_selected.connect(self.on_driver_selected)
        main_columns_layout.addWidget(self.leaderboard, stretch=0)

        # Middle Column (Flexible): Authentic Track View (top) + Waveform Graph (bottom)
        center_column_layout = QVBoxLayout()
        center_column_layout.setSpacing(8)
        center_column_layout.setContentsMargins(0, 0, 0, 0)

        self.track_view = TrackView(track_name=self.view_model.track_name, parent=self)
        self.track_view.set_track(self.view_model.track)

        self.telemetry_graph = TelemetryGraph(self)

        center_column_layout.addWidget(self.track_view, stretch=60)
        center_column_layout.addWidget(self.telemetry_graph, stretch=40)
        main_columns_layout.addLayout(center_column_layout, stretch=1)

        # Right Column (~360px): Selected Driver Status + Tyres + Powertrain
        right_column_widget = QWidget()
        right_column_widget.setFixedWidth(360)
        right_col_box = QVBoxLayout(right_column_widget)
        right_col_box.setContentsMargins(0, 0, 0, 0)
        right_col_box.setSpacing(8)

        self.race_status = RaceStatusPanel(self)
        self.tyre_card = TyreCard(self)
        self.energy_card = EnergyCard(self)
        self.fuel_card = self.energy_card

        right_col_box.addWidget(self.race_status, stretch=38)
        right_col_box.addWidget(self.tyre_card, stretch=34)
        right_col_box.addWidget(self.energy_card, stretch=28)

        main_columns_layout.addWidget(right_column_widget, stretch=0)

        content_layout.addLayout(main_columns_layout, stretch=1)

        # -------------------------------------------------------------
        # 3. Compact Bottom Telemetry Strip (86px)
        # -------------------------------------------------------------
        self.telemetry_panel = TelemetryPanel(self)
        content_layout.addWidget(self.telemetry_panel, stretch=0)

        root_layout.addWidget(content_container, 1)

        # Simulation Loop Timer (50ms = 20 Hz)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(50)

        # Initial tick to populate first frame
        self.update_simulation()

    def on_driver_selected(self, driver_name: str) -> None:
        """Handles driver selection from the leaderboard."""
        self.view_model.set_selected_driver(driver_name)
        self._refresh_ui()

    def on_circuit_selected(self, circuit_name: str) -> None:
        """Handles dynamic circuit switching from the TopBar selector."""
        new_track = TrackLibrary.get_track(circuit_name)
        self.view_model.set_track(new_track)
        self.track_view.set_track(new_track)
        self._refresh_ui()

    def toggle_pause_workbench(self) -> None:
        """Toggles simulation pause state and opens Setup Workbench dialog."""
        if not self.is_paused:
            self.pause_simulation()
            self.open_setup_workbench()
        else:
            self.resume_simulation()

    def pause_simulation(self) -> None:
        """Pauses the simulation timer and updates UI badge."""
        self.is_paused = True
        self.timer.stop()
        self._refresh_ui()

    def resume_simulation(self) -> None:
        """Resumes the simulation timer and updates UI badge."""
        self.is_paused = False
        self.timer.start(50)
        self._refresh_ui()

    def keyPressEvent(self, event):
        """Direct keyPressEvent fallback to ensure Space always toggles pause/workbench."""
        if event.key() == Qt.Key.Key_Space:
            self.toggle_pause_workbench()
            event.accept()
        else:
            super().keyPressEvent(event)

    def open_setup_workbench(self) -> None:
        """Displays the setup workbench modal dialog."""
        # Temporarily disable main window space shortcut while dialog is active
        self.space_shortcut.setEnabled(False)
        try:
            dialog = SetupWorkbenchDialog(self.view_model, self)
            dialog.resume_requested.connect(self.resume_simulation)
            dialog.exec()
        finally:
            self.space_shortcut.setEnabled(True)
            self.setFocus()
            self._refresh_ui()

    def update_simulation(self) -> None:
        """Step the simulation and update all UI views."""
        # 50 ms time step
        self.view_model.tick(0.05)
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        """Pushes latest view-model snapshots to all subwidgets."""
        selected_snapshot = self.view_model.get_selected_snapshot()
        all_snapshots = self.view_model.get_all_snapshots()
        leaderboard_entries = self.view_model.get_leaderboard()

        current_lap = selected_snapshot.current_lap if selected_snapshot else 1
        is_finished = self.view_model.is_finished

        # 1. Top Bar
        self.top_bar.update_state(
            current_lap=current_lap,
            total_laps=self.view_model.total_laps,
            elapsed_seconds=self.view_model.elapsed_time,
            is_finished=is_finished,
            is_paused=self.is_paused,
        )

        # 2. Leaderboard
        self.leaderboard.update_standings(leaderboard_entries)

        # 3. Track Visualization
        car_markers: list[CarMarkerData] = [
            CarMarkerData(
                driver_name=s.name,
                driver_number=s.number,
                progress=s.track_progress,
                color_hex=s.color,
                is_selected=(s.name == self.view_model.selected_driver_name),
            )
            for s in all_snapshots
        ]
        self.track_view.update_cars(car_markers)

        # 4. Race Status
        self.race_status.update_status(selected_snapshot)

        # 5. Telemetry Waveform Graph
        active_driver_name = self.view_model.selected_driver_name
        history = self.view_model.get_speed_history(active_driver_name)
        color = selected_snapshot.color if selected_snapshot else THEME.CYAN
        self.telemetry_graph.update_graph(history, color)

        # 6. Tyre & Powertrain/Energy Cards
        self.tyre_card.update_tyres(selected_snapshot)
        self.energy_card.update_energy(selected_snapshot)

        # 7. Bottom Telemetry Strip (6 key metrics)
        self.telemetry_panel.update_telemetry(selected_snapshot)
