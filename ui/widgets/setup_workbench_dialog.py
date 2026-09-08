"""Race Control & Car Setup Workbench Modal Dialog."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ui.theme import FONT_FAMILY_MONO, THEME
from ui.view_models.race_view_model import RaceViewModel
from ui.widgets.car_setup_view import CarSetupView


class SetupSliderControl(QWidget):
    """Reusable synchronized Slider + SpinBox control."""

    valueChanged = Signal(float)

    def __init__(
        self,
        label: str,
        min_val: float,
        max_val: float,
        step: float = 0.1,
        initial_val: float = 0.0,
        unit: str = "",
        decimals: int = 1,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.step = step
        self.decimals = decimals
        self._multiplier = 10**decimals

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(10)

        # Label
        self.label_widget = QLabel(label.upper())
        self.label_widget.setFixedWidth(130)
        self.label_widget.setStyleSheet(
            f"font-size: 10px; font-weight: 700; color: {THEME.TEXT_SECONDARY}; letter-spacing: 0.8px;"
        )

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(min_val * self._multiplier), int(max_val * self._multiplier))
        self.slider.setValue(int(initial_val * self._multiplier))
        self.slider.setStyleSheet(
            f"""
            QSlider::groove:horizontal {{
                height: 4px;
                background: {THEME.BORDER_SUBTLE};
                border-radius: 2px;
            }}
            QSlider::sub-page:horizontal {{
                background: {THEME.CYAN};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {THEME.TEXT_PRIMARY};
                border: 1px solid {THEME.BORDER_MUTED};
                width: 14px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 7px;
            }}
            """
        )

        # SpinBox
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(min_val, max_val)
        self.spinbox.setSingleStep(step)
        self.spinbox.setDecimals(decimals)
        self.spinbox.setValue(initial_val)
        if unit:
            self.spinbox.setSuffix(f" {unit}")
        self.spinbox.setFixedWidth(95)
        self.spinbox.setStyleSheet(
            f"""
            QDoubleSpinBox {{
                background-color: {THEME.BG_BASE};
                border: 1px solid {THEME.BORDER_SUBTLE};
                border-radius: 4px;
                color: {THEME.TEXT_PRIMARY};
                font-family: {FONT_FAMILY_MONO};
                font-size: 11px;
                padding: 3px 6px;
            }}
            QDoubleSpinBox:focus {{
                border-color: {THEME.CYAN};
            }}
            """
        )

        # Sync slider and spinbox
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)

        layout.addWidget(self.label_widget)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.spinbox)

    def _on_slider_changed(self, int_val: int):
        val = int_val / self._multiplier
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(val)
        self.spinbox.blockSignals(False)
        self.valueChanged.emit(val)

    def _on_spinbox_changed(self, float_val: float):
        int_val = int(float_val * self._multiplier)
        self.slider.blockSignals(True)
        self.slider.setValue(int_val)
        self.slider.blockSignals(False)
        self.valueChanged.emit(float_val)

    def value(self) -> float:
        return self.spinbox.value()

    def setValue(self, val: float):
        self.spinbox.setValue(val)


class SetupWorkbenchDialog(QDialog):
    """Interactive Modal Workbench for tuning race car and driver parameters live."""

    setup_applied = Signal(str, dict)
    resume_requested = Signal()

    def __init__(self, view_model: RaceViewModel, parent: QWidget | None = None):
        super().__init__(parent)
        self.view_model = view_model
        self.setWindowTitle("Race Control // Car Setup & Diagnostic Workbench")
        self.setMinimumSize(920, 620)
        self.setModal(True)

        self.current_driver_name = self.view_model.selected_driver_name or "Driver A"

        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {THEME.BG_BASE};
                color: {THEME.TEXT_PRIMARY};
            }}
            QGroupBox {{
                background-color: {THEME.BG_SURFACE};
                border: 1px solid {THEME.BORDER_SUBTLE};
                border-radius: 6px;
                margin-top: 12px;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 1px;
                color: {THEME.TEXT_SECONDARY};
                padding-top: 18px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
            }}
            """
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 14, 18, 14)
        root_layout.setSpacing(12)

        # -------------------------------------------------------------
        # 1. TOP HEADER & DRIVER SELECTOR
        # -------------------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("RACE CONTROL // SETUP & DIAGNOSTICS WORKBENCH")
        title.setStyleSheet(f"font-size: 13px; font-weight: 800; letter-spacing: 1.2px; color: {THEME.TEXT_PRIMARY};")
        sub = QLabel("LIVE SIMULATION PAUSED • REAL-TIME PARAMETER TUNING")
        sub.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {THEME.AMBER}; letter-spacing: 0.8px;")
        title_box.addWidget(title)
        title_box.addWidget(sub)

        header_layout.addLayout(title_box)
        header_layout.addStretch(1)

        # Driver Toggle Buttons
        self.btn_driver_a = QPushButton("#07 DRIVER A")
        self.btn_driver_b = QPushButton("#22 DRIVER B")
        self.btn_driver_a.setCheckable(True)
        self.btn_driver_b.setCheckable(True)
        self.btn_driver_a.clicked.connect(lambda: self.switch_driver("Driver A"))
        self.btn_driver_b.clicked.connect(lambda: self.switch_driver("Driver B"))

        header_layout.addWidget(self.btn_driver_a)
        header_layout.addWidget(self.btn_driver_b)

        root_layout.addLayout(header_layout)

        # Divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {THEME.BORDER_SUBTLE};")
        root_layout.addWidget(divider)

        # -------------------------------------------------------------
        # 2. MAIN 2-COLUMN CONTENT
        # -------------------------------------------------------------
        main_content = QHBoxLayout()
        main_content.setSpacing(16)

        # --- LEFT: 2D Chassis Visualization ---
        left_box = QVBoxLayout()
        left_box.setSpacing(8)

        self.chassis_view = CarSetupView(self)
        left_box.addWidget(self.chassis_view, 1)

        main_content.addLayout(left_box, stretch=42)

        # --- RIGHT: Parameter Controls ---
        right_box = QVBoxLayout()
        right_box.setSpacing(10)

        # Group 1: Powertrain & Dynamics
        grp_powertrain = QGroupBox("1. POWERTRAIN & LONGITUDINAL DYNAMICS")
        layout_pt = QVBoxLayout(grp_powertrain)
        layout_pt.setSpacing(8)

        self.ctrl_max_speed = SetupSliderControl("Max Top Speed", 280.0, 360.0, step=1.0, initial_val=318.0, unit="km/h", decimals=1)
        self.ctrl_acceleration = SetupSliderControl("Engine Accel", 8.0, 16.0, step=0.1, initial_val=12.4, unit="m/s²", decimals=1)
        self.ctrl_braking_force = SetupSliderControl("Braking Decel", 30.0, 55.0, step=0.5, initial_val=42.0, unit="m/s²", decimals=1)

        layout_pt.addWidget(self.ctrl_max_speed)
        layout_pt.addWidget(self.ctrl_acceleration)
        layout_pt.addWidget(self.ctrl_braking_force)
        right_box.addWidget(grp_powertrain)

        # Group 2: Tires & Aerodynamics
        grp_aero = QGroupBox("2. TIRE GRIP & AERODYNAMICS")
        layout_aero = QVBoxLayout(grp_aero)
        layout_aero.setSpacing(8)

        self.ctrl_grip = SetupSliderControl("Mechanical Grip (μ)", 1.20, 2.20, step=0.05, initial_val=1.75, unit="μ", decimals=2)

        df_row = QHBoxLayout()
        lbl_df = QLabel("DOWNFORCE PACKAGE")
        lbl_df.setFixedWidth(130)
        lbl_df.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {THEME.TEXT_SECONDARY}; letter-spacing: 0.8px;")

        self.combo_downforce = QComboBox()
        self.combo_downforce.addItems([
            "Medium Downforce (Standard GP)",
            "High Downforce (Monaco - Max Grip)",
            "Low Downforce (Monza - Low Drag)",
        ])
        self.combo_downforce.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {THEME.BG_BASE};
                border: 1px solid {THEME.BORDER_SUBTLE};
                border-radius: 4px;
                color: {THEME.TEXT_PRIMARY};
                font-size: 11px;
                padding: 4px 10px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            """
        )
        df_row.addWidget(lbl_df)
        df_row.addWidget(self.combo_downforce, 1)

        layout_aero.addWidget(self.ctrl_grip)
        layout_aero.addLayout(df_row)

        # Strategic Tyre Compound & Pit Stop Controls
        strat_row = QHBoxLayout()
        lbl_strat = QLabel("NEXT PIT COMPOUND")
        lbl_strat.setFixedWidth(130)
        lbl_strat.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {THEME.TEXT_SECONDARY}; letter-spacing: 0.8px;")

        self.combo_compound = QComboBox()
        self.combo_compound.addItems([
            "Soft (C3 - Red, High Grip, Fast Deg)",
            "Medium (C2 - Yellow, Balanced GP)",
            "Hard (C1 - White, High Durability)",
        ])
        self.combo_compound.setCurrentIndex(1)
        self.combo_compound.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {THEME.BG_BASE};
                border: 1px solid {THEME.BORDER_SUBTLE};
                border-radius: 4px;
                color: {THEME.TEXT_PRIMARY};
                font-size: 11px;
                padding: 4px 10px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            """
        )
        strat_row.addWidget(lbl_strat)
        strat_row.addWidget(self.combo_compound, 1)

        self.btn_call_pit = QPushButton("⚠ CALL BOX BOX (PIT STOP THIS LAP)")
        self.btn_call_pit.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 159, 28, 0.15);
                border: 1px solid {THEME.AMBER};
                color: {THEME.AMBER};
                font-family: {FONT_FAMILY_MONO};
                font-size: 11px;
                font-weight: 800;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 159, 28, 0.30);
            }}
            """
        )
        self.btn_call_pit.clicked.connect(self.on_call_pit_stop)

        layout_aero.addLayout(strat_row)
        layout_aero.addWidget(self.btn_call_pit)
        right_box.addWidget(grp_aero)

        # Group 3: Driver Behavior Modifiers
        grp_driver = QGroupBox("3. DRIVER BEHAVIOR MODIFIERS")
        layout_dr = QVBoxLayout(grp_driver)
        layout_dr.setSpacing(8)

        self.ctrl_braking_skill = SetupSliderControl("Late Braking Skill", 0.0, 1.0, step=0.01, initial_val=0.88, unit="", decimals=2)
        self.ctrl_aggression = SetupSliderControl("Throttle Aggression", 0.0, 1.0, step=0.01, initial_val=0.82, unit="", decimals=2)

        layout_dr.addWidget(self.ctrl_braking_skill)
        layout_dr.addWidget(self.ctrl_aggression)
        right_box.addWidget(grp_driver)

        right_box.addStretch(1)
        main_content.addLayout(right_box, stretch=58)

        root_layout.addLayout(main_content, 1)

        # -------------------------------------------------------------
        # 3. ACTION BUTTONS FOOTER
        # -------------------------------------------------------------
        footer_divider = QFrame()
        footer_divider.setFixedHeight(1)
        footer_divider.setStyleSheet(f"background-color: {THEME.BORDER_SUBTLE};")
        root_layout.addWidget(footer_divider)

        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(10)

        self.btn_reset = QPushButton("↺ RESET DEFAULTS")
        self.btn_reset.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {THEME.BG_SURFACE};
                border: 1px solid {THEME.BORDER_MUTED};
                color: {THEME.TEXT_SECONDARY};
                padding: 8px 16px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {THEME.BG_SURFACE_HOVER};
                color: {THEME.TEXT_PRIMARY};
            }}
            """
        )
        self.btn_reset.clicked.connect(self.on_reset_defaults)

        self.btn_apply = QPushButton("APPLY SETUP")
        self.btn_apply.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {THEME.BG_SURFACE_ELEVATED};
                border: 1px solid {THEME.CYAN};
                color: {THEME.CYAN};
                padding: 8px 18px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 229, 255, 0.15);
            }}
            """
        )
        self.btn_apply.clicked.connect(self.on_apply)

        self.btn_apply_resume = QPushButton("▶ APPLY & RESUME RACE")
        self.btn_apply_resume.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {THEME.GREEN};
                border: 1px solid {THEME.GREEN};
                color: #06110A;
                padding: 8px 22px;
                font-size: 12px;
                font-weight: 800;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #00FF88;
            }}
            """
        )
        self.btn_apply_resume.clicked.connect(self.on_apply_and_resume)

        self.btn_close = QPushButton("CANCEL")
        self.btn_close.clicked.connect(self.reject)

        footer_layout.addWidget(self.btn_reset)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.btn_close)
        footer_layout.addWidget(self.btn_apply)
        footer_layout.addWidget(self.btn_apply_resume)

        root_layout.addLayout(footer_layout)

        # Load initial values
        self.switch_driver(self.current_driver_name)

    def switch_driver(self, driver_name: str) -> None:
        """Loads and visualizes setup for the selected driver."""
        self.current_driver_name = driver_name
        is_driver_a = (driver_name == "Driver A")

        # Update buttons
        self.btn_driver_a.setChecked(is_driver_a)
        self.btn_driver_b.setChecked(not is_driver_a)

        color_a = THEME.CYAN
        color_b = THEME.AMBER

        if is_driver_a:
            self.btn_driver_a.setStyleSheet(f"background-color: {color_a}22; border: 1px solid {color_a}; color: {color_a}; font-weight: 800;")
            self.btn_driver_b.setStyleSheet(f"background-color: {THEME.BG_SURFACE}; border: 1px solid {THEME.BORDER_SUBTLE}; color: {THEME.TEXT_MUTED};")
            self.chassis_view.set_driver("Driver A", 7, color_a)
        else:
            self.btn_driver_b.setStyleSheet(f"background-color: {color_b}22; border: 1px solid {color_b}; color: {color_b}; font-weight: 800;")
            self.btn_driver_a.setStyleSheet(f"background-color: {THEME.BG_SURFACE}; border: 1px solid {THEME.BORDER_SUBTLE}; color: {THEME.TEXT_MUTED};")
            self.chassis_view.set_driver("Driver B", 22, color_b)

        # Load car setup
        setup = self.view_model.get_car_setup(driver_name)
        if setup:
            self.ctrl_max_speed.setValue(setup.get("max_speed", 320.0))
            self.ctrl_acceleration.setValue(setup.get("acceleration", 12.0))
            self.ctrl_braking_force.setValue(setup.get("max_brake_decel", 42.0))

            # Convert grip_multiplier back to mechanical grip mu (base 1.75)
            grip_mult = setup.get("grip_multiplier", 1.0)
            self.ctrl_grip.setValue(round(1.75 * grip_mult, 2))

            df_level = setup.get("downforce_level", "Medium")
            if df_level == "High":
                self.combo_downforce.setCurrentIndex(1)
            elif df_level == "Low":
                self.combo_downforce.setCurrentIndex(2)
            else:
                self.combo_downforce.setCurrentIndex(0)

            self.ctrl_braking_skill.setValue(setup.get("braking_skill", 0.85))
            self.ctrl_aggression.setValue(setup.get("aggression", 0.70))

        # Reset Call Box button state
        self.btn_call_pit.setText("⚠ CALL BOX BOX (PIT STOP THIS LAP)")
        self.btn_call_pit.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(255, 159, 28, 0.15);
                border: 1px solid {THEME.AMBER};
                color: {THEME.AMBER};
                font-family: {FONT_FAMILY_MONO};
                font-size: 11px;
                font-weight: 800;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 159, 28, 0.30);
            }}
            """
        )

        # Update tyre telemetry
        snap = self.view_model.get_selected_snapshot()
        if snap:
            self.chassis_view.set_tyre_telemetry_4w(
                getattr(snap, "fl_temp", snap.tyre_temperature),
                getattr(snap, "fr_temp", snap.tyre_temperature),
                getattr(snap, "rl_temp", snap.tyre_temperature),
                getattr(snap, "rr_temp", snap.tyre_temperature),
                getattr(snap, "fl_wear", snap.tyre_wear),
                getattr(snap, "fr_wear", snap.tyre_wear),
                getattr(snap, "rl_wear", snap.tyre_wear),
                getattr(snap, "rr_wear", snap.tyre_wear),
            )

    def on_call_pit_stop(self) -> None:
        """Dispatches a manual pit box command for the selected driver."""
        comp_str = self.combo_compound.currentText()
        next_comp = "Soft" if "Soft" in comp_str else ("Hard" if "Hard" in comp_str else "Medium")
        if hasattr(self.view_model, "request_pit_stop"):
            self.view_model.request_pit_stop(self.current_driver_name, next_comp)
            self.btn_call_pit.setText(f"✓ BOX CONFIRMED ({next_comp.upper()} READY)")
            self.btn_call_pit.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: rgba(0, 230, 118, 0.20);
                    border: 1px solid {THEME.GREEN};
                    color: {THEME.GREEN};
                    font-family: {FONT_FAMILY_MONO};
                    font-size: 11px;
                    font-weight: 800;
                    padding: 6px 12px;
                    border-radius: 4px;
                }}
                """
            )

    def _collect_setup_dict(self) -> dict:
        df_text = self.combo_downforce.currentText()
        if "High" in df_text:
            df_pkg = "High"
        elif "Low" in df_text:
            df_pkg = "Low"
        else:
            df_pkg = "Medium"

        # Calculate grip multiplier relative to 1.75 base
        mu_val = self.ctrl_grip.value()
        grip_mult = max(0.5, mu_val / 1.75)

        return {
            "max_speed": self.ctrl_max_speed.value(),
            "acceleration": self.ctrl_acceleration.value(),
            "max_brake_decel": self.ctrl_braking_force.value(),
            "grip_multiplier": grip_mult,
            "downforce_level": df_pkg,
            "braking_skill": self.ctrl_braking_skill.value(),
            "aggression": self.ctrl_aggression.value(),
        }

    def on_apply(self) -> None:
        setup = self._collect_setup_dict()
        self.view_model.apply_car_setup(self.current_driver_name, setup)
        self.setup_applied.emit(self.current_driver_name, setup)

    def on_apply_and_resume(self) -> None:
        self.on_apply()
        self.resume_requested.emit()
        self.accept()

    def on_reset_defaults(self) -> None:
        self.view_model.reset_car_setup(self.current_driver_name)
        self.switch_driver(self.current_driver_name)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            focused = self.focusWidget()
            if isinstance(focused, (QDoubleSpinBox, QComboBox)):
                super().keyPressEvent(event)
                return
            self.on_apply_and_resume()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
        else:
            super().keyPressEvent(event)
