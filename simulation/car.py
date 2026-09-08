"""Car Physical Model and Autonomous Driving Controller."""

import math
from dataclasses import dataclass, field
from typing import Any

from .tyre import CompoundType, TyreSet


@dataclass
class Car:
    """Represents a racing car with longitudinal dynamics, aero drag, and braking AI."""

    name: str
    driver: Any

    max_speed: float = 320.0  # km/h
    acceleration: float = 12.0  # max engine acceleration m/s^2

    position: float = 0.0  # meters along the circuit
    speed_ms: float = 0.0  # SI internal speed in m/s

    throttle: float = 0.0  # 0.0 to 1.0
    brake: float = 0.0  # 0.0 to 1.0

    gear: int = 1
    rpm: float = 4000.0

    # Physical parameters
    max_brake_decel: float = 42.0  # m/s^2 (~4.3G F1-grade braking)
    drag_coeff: float = 0.00038  # Calibrated aero drag factor
    rolling_resistance: float = 0.15  # m/s^2 mechanical resistance
    grip_multiplier: float = 1.0  # Mechanical grip scalar (relative to track base mu)
    downforce_level: str = "Medium"  # "High", "Medium", "Low"

    tyres: TyreSet = field(default_factory=TyreSet)

    # 2026 Regulations: Active Aero (Z-Mode / X-Mode) & Slipstream
    aero_mode: str = "Z-MODE"  # "Z-MODE" (Cornering/Braking) or "X-MODE" (Straight/Low Drag)
    aero_mode_hold_timer: float = 1.0  # Dwell time in current aero mode for debouncing (s)
    slipstream_reduction: float = 0.0  # 0.15 to 0.35 drag reduction when trailing in straight
    in_dirty_air: bool = False  # 10% downforce penalty when trailing in corners
    _in_braking_zone: bool = False  # Hysteresis latch for corner approach braking

    # 2026 Regulations: Hybrid ERS (4.0 MJ Battery Depot & Manual Override Mode)
    ers_max_energy_mj: float = 4.0
    ers_energy_mj: float = 3.4  # Initial charge 85% = 3.4 MJ
    ers_status: str = "IDLE"  # "REGEN", "DEPLOY", "MOM ACTIVE", "IDLE"
    override_ready: bool = False
    mom_active: bool = False

    # V0.6 Race Strategy, Dynamic Pit Stop & Tyre Compound Engine
    pit_requested: bool = False
    next_compound: CompoundType = field(default=CompoundType.MEDIUM)
    in_pit_lane: bool = False
    pit_state: str = "RACING"  # "RACING", "ENTERING_PIT", "IN_BOX_STOP", "EXITING_PIT"
    pit_stop_timer: float = 0.0
    pit_lane_distance: float = 0.0
    pit_stops: int = 0

    # Fuel mass and deterministic consumption
    fuel: float = 100.0  # Initial 100.0 kg
    fuel_flow_kgh: float = 0.0  # kg/h flow rate
    dry_mass_kg: float = 798.0  # FIA minimum dry car + driver mass (kg)

    _defaults_captured: bool = False
    _default_setup: dict | None = None

    @property
    def total_mass_kg(self) -> float:
        """Total dynamic vehicle mass including instantaneous fuel load (kg)."""
        return self.dry_mass_kg + max(0.0, self.fuel)

    @property
    def mass_factor(self) -> float:
        """Inertial acceleration, braking, and load scaling relative to baseline (798kg dry + 10kg fuel).

        Calibrated to reflect empirical high-downforce F1 behavior where total vertical load
        is dominated by aerodynamic downforce (~2500kg), yielding ~0.33 - 0.38 s / 10 kg lap time delta.
        """
        base_mass = self.dry_mass_kg + 10.0
        fuel_excess = max(0.0, self.fuel - 10.0)
        return max(0.6, min(1.1, base_mass / (base_mass + fuel_excess * 0.65)))

    @property
    def ers_soc_pct(self) -> float:
        """ERS Battery State of Charge percentage (%0 to %100)."""
        return max(0.0, min(100.0, (self.ers_energy_mj / self.ers_max_energy_mj) * 100.0))

    def __post_init__(self):
        if not hasattr(self, "tyres") or self.tyres is None:
            self.tyres = TyreSet()
        if not self._defaults_captured:
            self._default_setup = self.get_setup_dict()
            self._defaults_captured = True

    def get_setup_dict(self) -> dict:
        """Returns current car and driver setup parameters."""
        return {
            "max_speed": float(self.max_speed),
            "acceleration": float(self.acceleration),
            "max_brake_decel": float(self.max_brake_decel),
            "grip_multiplier": float(self.grip_multiplier),
            "downforce_level": str(self.downforce_level),
            "braking_skill": float(getattr(self.driver, "braking_skill", 0.85)),
            "aggression": float(getattr(self.driver, "aggression", 0.70)),
        }

    def apply_setup_dict(self, setup: dict) -> None:
        """Applies new setup parameters to car dynamics and driver behavior."""
        if "max_speed" in setup:
            self.max_speed = float(setup["max_speed"])
        if "acceleration" in setup:
            self.acceleration = float(setup["acceleration"])
        if "max_brake_decel" in setup:
            self.max_brake_decel = float(setup["max_brake_decel"])
        if "grip_multiplier" in setup:
            self.grip_multiplier = float(setup["grip_multiplier"])
        if "downforce_level" in setup:
            self.downforce_level = str(setup["downforce_level"])
            if self.downforce_level == "Low":
                self.drag_coeff = 0.00030
            elif self.downforce_level == "High":
                self.drag_coeff = 0.00048
            else:
                self.drag_coeff = 0.00038

        # Driver traits
        if "braking_skill" in setup and hasattr(self.driver, "braking_skill"):
            self.driver.braking_skill = max(0.0, min(1.0, float(setup["braking_skill"])))
        if "aggression" in setup and hasattr(self.driver, "aggression"):
            self.driver.aggression = max(0.0, min(1.0, float(setup["aggression"])))

    def reset_to_defaults(self) -> None:
        """Restores factory default setup parameters."""
        if self._default_setup:
            self.apply_setup_dict(self._default_setup)

    @property
    def speed(self) -> float:
        """Current speed in km/h for UI, Telemetry, and backwards compatibility."""
        return self.speed_ms * 3.6

    @speed.setter
    def speed(self, val_kmh: float):
        self.speed_ms = max(0.0, val_kmh / 3.6)

    @property
    def max_speed_ms(self) -> float:
        return self.max_speed / 3.6

    def update(self, dt: float, track: Any, manual_inputs: bool = False) -> bool:
        """Advances vehicle physics by dt seconds along the given track."""
        if isinstance(track, (int, float)):
            track_length = float(track)
            track_obj = None
        else:
            track_length = track.length
            track_obj = track

        current_segment = None
        if track_obj and hasattr(track_obj, "get_segment"):
            current_segment = track_obj.get_segment(self.position)

        is_straight = (current_segment.type == "straight") if current_segment else True
        steering_straight = (getattr(current_segment, "direction", "straight") == "straight") if current_segment else True

        # Pit Lane entry trigger
        if not self.in_pit_lane and self.pit_requested:
            pit_entry_threshold = track_length - 260.0
            if self.position >= pit_entry_threshold:
                self.in_pit_lane = True
                self.pit_state = "ENTERING_PIT"
                self.pit_lane_distance = 0.0
                self.pit_requested = False
                # Pit limiter active across pit entry line (80 km/h = 22.22 m/s)
                self.speed_ms = min(self.speed_ms, 80.0 / 3.6)

        if self.in_pit_lane:
            self.aero_mode = "Z-MODE"
            self.mom_active = False
            self.override_ready = False

            if self.pit_state == "ENTERING_PIT":
                self.pit_lane_distance += self.speed_ms * dt
                if self.pit_lane_distance >= 220.0:
                    self.pit_state = "IN_BOX_STOP"
                    self.pit_stop_timer = 2.4
                    self.speed_ms = 0.0
            elif self.pit_state == "IN_BOX_STOP":
                self.speed_ms = 0.0
                self.pit_stop_timer -= dt
                if self.pit_stop_timer <= 0.0:
                    # Stationary tyre change complete
                    if hasattr(self, "tyres") and self.tyres:
                        self.tyres.change_compound(self.next_compound, initial_temp=80.0)
                    self.pit_stops += 1
                    self.pit_state = "EXITING_PIT"
            elif self.pit_state == "EXITING_PIT":
                self.pit_lane_distance += self.speed_ms * dt
                if self.pit_lane_distance >= 440.0:
                    self.in_pit_lane = False
                    self.pit_state = "RACING"
                    self.pit_lane_distance = 0.0

        # 1. Driver AI Decision (Throttle vs Brake Target)
        if not manual_inputs:
            self._compute_driver_inputs(track_obj)

        # Check upcoming corner distance to deploy downforce before corner entry
        approaching_corner = False
        if track_obj and hasattr(track_obj, "get_upcoming_corners"):
            upcoming = track_obj.get_upcoming_corners(self.position, horizon_m=50.0)
            if upcoming:
                dist_to_corner = upcoming[0][1]
                if dist_to_corner <= 35.0:
                    approaching_corner = True

        # Advance Active Aero state dwell timer
        self.aero_mode_hold_timer += dt

        # 2026 Active Aero (Z-Mode vs X-Mode) & MOM Mode Evaluation
        if self.in_pit_lane or self.brake > 0.01 or not is_straight or approaching_corner or not steering_straight:
            # Revert instantly without delay upon braking, approaching/in corners, or in pit lane (Safety Lock)
            if self.aero_mode != "Z-MODE":
                self.aero_mode = "Z-MODE"
                self.aero_mode_hold_timer = 0.0
            self.mom_active = False
        else:
            # On straightaway: apply debounce dwell time (0.40s) and throttle hysteresis ([0.85, 0.95])
            if self.aero_mode == "Z-MODE":
                if self.throttle >= 0.95 and self.aero_mode_hold_timer >= 0.40:
                    self.aero_mode = "X-MODE"
                    self.aero_mode_hold_timer = 0.0
            elif self.aero_mode == "X-MODE":
                if self.throttle < 0.85 and self.aero_mode_hold_timer >= 0.40:
                    self.aero_mode = "Z-MODE"
                    self.aero_mode_hold_timer = 0.0

        if not is_straight or self.in_pit_lane or self.ers_soc_pct < 10.0 or self.brake > 0.01 or (self.mom_active and self.speed_ms < 272.0 / 3.6):
            self.mom_active = False

        # 2. Longitudinal Vehicle Physics Integration
        self._integrate_physics(dt, is_straight)

        # 3. Dynamic 4-Wheel Tyre Thermal & Wear Integration
        corner_radius = current_segment.radius if (current_segment and current_segment.type == "corner") else None
        turn_direction = getattr(current_segment, "direction", "straight") if current_segment else "straight"
        driver_tyre_mgmt = getattr(self.driver, "tyre_management", 0.85)

        if hasattr(self, "tyres") and self.tyres:
            self.tyres.update(
                dt=dt,
                speed_ms=self.speed_ms,
                brake=self.brake,
                throttle=self.throttle,
                corner_radius=corner_radius,
                turn_direction=turn_direction,
                driver_tyre_mgmt=driver_tyre_mgmt,
            )

        # 4. Transmission & RPM Update
        self._update_transmission()

        # 5. Track Distance Advancement & Lap Wrap
        self.position += self.speed_ms * dt
        if self.position >= track_length:
            self.position -= track_length
            return True

        return False

    def reset_race_state(self) -> None:
        """Resets car position, telemetry dynamics, and tyres to initial race start."""
        self.position = 0.0
        self.speed_ms = 0.0
        self.throttle = 0.0
        self.brake = 0.0
        self.gear = 1
        self.rpm = 4000.0
        self.ers_energy_mj = 3.4
        self.ers_status = "IDLE"
        self.aero_mode = "Z-MODE"
        self.aero_mode_hold_timer = 1.0
        self._in_braking_zone = False
        self.override_ready = False
        self.mom_active = False
        self.slipstream_reduction = 0.0
        self.in_dirty_air = False
        self.fuel = 100.0
        self.fuel_flow_kgh = 0.0
        self.pit_requested = False
        self.in_pit_lane = False
        self.pit_state = "RACING"
        self.pit_stop_timer = 0.0
        self.pit_lane_distance = 0.0
        self.pit_stops = 0
        if hasattr(self, "tyres") and self.tyres:
            self.tyres.reset(initial_temp=80.0)

    def _compute_driver_inputs(self, track_obj: Any | None) -> None:
        """Determines throttle and brake application using kinematic braking calculations."""
        # 0. Pit Lane Speed Limiter (80 km/h = 22.22 m/s) & Box Stop
        if self.in_pit_lane:
            pit_limiter_ms = 80.0 / 3.6  # 22.222 m/s
            if self.pit_state == "IN_BOX_STOP":
                self.throttle = 0.0
                self.brake = 1.0
                self.speed_ms = 0.0
            elif self.speed_ms > pit_limiter_ms + 0.1:
                self.throttle = 0.0
                self.brake = min(1.0, (self.speed_ms - pit_limiter_ms) / 1.5)
            elif self.speed_ms < pit_limiter_ms - 0.5:
                self.throttle = 0.80
                self.brake = 0.0
            else:
                self.throttle = 0.12
                self.brake = 0.0
            return

        if track_obj is None or not hasattr(track_obj, "get_upcoming_corners"):
            # Fallback for plain straight tracks
            if self.speed_ms < self.max_speed_ms:
                self.throttle = 1.0
                self.brake = 0.0
            else:
                self.throttle = 0.5
                self.brake = 0.0
            return

        # Effective braking capability influenced by driver braking skill and vehicle mass
        skill_multiplier = 0.85 + (getattr(self.driver, "braking_skill", 0.85) * 0.15)
        effective_brake_decel = self.max_brake_decel * skill_multiplier * self.mass_factor

        # Check upcoming corners within 450m horizon
        upcoming = track_obj.get_upcoming_corners(self.position, horizon_m=450.0)

        should_brake = False
        target_brake_pressure = 0.0

        for corner, dist in upcoming:
            # Target apex speed with grip multiplier, downforce package, tyre thermal grip, and driver consistency variance
            consistency = getattr(self.driver, "consistency", 0.9)
            downforce_bonus = 1.08 if self.downforce_level == "High" else (0.94 if self.downforce_level == "Low" else 1.00)

            # Dirty Air effect in cornering: 10% downforce reduction
            if self.in_dirty_air:
                downforce_bonus *= 0.90

            tyre_grip = self.tyres.get_compound_grip() if (hasattr(self, "tyres") and self.tyres) else 1.0
            grip_factor = math.sqrt(max(0.2, self.grip_multiplier * tyre_grip)) * (self.mass_factor ** 0.5)
            target_v = corner.apex_speed_ms * grip_factor * downforce_bonus * (0.98 + 0.04 * (consistency - 0.9))

            if dist == 0.0:
                self._in_braking_zone = False
                # Currently inside corner: check progress past apex
                norm_pos = self.position % track_obj.length
                corner_prog = (norm_pos - corner.start_pos) / max(1.0, corner.length)

                if self.speed_ms > target_v * 1.03:
                    # Too fast entering corner - trail brake
                    should_brake = True
                    target_brake_pressure = min(0.65, (self.speed_ms - target_v) / 4.0)
                elif corner_prog > 0.30:
                    # Past apex: smoothly roll on throttle towards corner exit
                    aggression = getattr(self.driver, "aggression", 0.7)
                    exit_throttle = 0.60 + (0.40 * corner_prog) * (0.85 + 0.15 * aggression)
                    self.throttle = min(1.0, exit_throttle)
                    self.brake = 0.0
                    return
                else:
                    # Approaching or at apex: maintenance throttle
                    self.throttle = 0.45
                    self.brake = 0.0
                    return
                break
            else:
                # Approaching corner - compute required braking distance
                if self.speed_ms > target_v:
                    # d_brake = (v_cur^2 - v_target^2) / (2 * a_brake)
                    v_diff_sq = (self.speed_ms * self.speed_ms) - (target_v * target_v)
                    d_req = v_diff_sq / (2.0 * effective_brake_decel)

                    # Braking point margin: skilled drivers brake later
                    braking_skill = getattr(self.driver, "braking_skill", 0.85)
                    safety_margin = 1.04 - (braking_skill - 0.8) * 0.08
                    d_trigger = d_req * safety_margin

                    # Hysteresis latch: once braking is initiated, sustain through the deceleration zone
                    if (self._in_braking_zone and dist <= d_trigger * 1.50) or (dist <= d_trigger):
                        self._in_braking_zone = True
                        should_brake = True
                        urgency = max(0.70, min(1.0, (d_trigger / max(1.0, dist)) * 0.95))
                        target_brake_pressure = max(target_brake_pressure, urgency)
                        break
                else:
                    self._in_braking_zone = False

        if should_brake:
            self.throttle = 0.0
            self.brake = target_brake_pressure
        else:
            self._in_braking_zone = False
            # Full acceleration along straights
            self.brake = 0.0
            self.throttle = 1.0

    def _integrate_physics(self, dt: float, is_straight: bool = True) -> None:
        """Applies engine force, drag, ERS hybrid deploy/regen, and braking to update speed_ms."""
        # 2026 Aerodynamic drag coefficient factoring Active Aero & Slipstream
        aero_mult = 1.0
        if self.aero_mode == "X-MODE":
            aero_mult *= 0.60  # 40% reduction in X-Mode
        if self.slipstream_reduction > 0.0:
            aero_mult *= max(0.0, 1.0 - self.slipstream_reduction)

        effective_drag_coeff = self.drag_coeff * aero_mult
        a_drag = (effective_drag_coeff * self.speed_ms * self.speed_ms) + self.rolling_resistance

        # Stationary Box Stop handling
        if self.in_pit_lane and self.pit_state == "IN_BOX_STOP":
            self.speed_ms = 0.0
            self.fuel_flow_kgh = 0.0
            return

        if self.brake > 0.01:
            skill_mult = 0.85 + (getattr(self.driver, "braking_skill", 0.85) * 0.15)
            actual_brake_accel = self.max_brake_decel * skill_mult * self.brake * self.mass_factor
            brake_decel = actual_brake_accel + a_drag
            self.speed_ms = max(0.0, self.speed_ms - brake_decel * dt)

            # MGU-K Kinetic Energy Regeneration (P_regen proportional to a_brake * v)
            # Max 350 kW recovery under 2026 technical regulations
            p_regen_kw = min(350.0, 0.16 * actual_brake_accel * self.speed_ms)
            p_regen_mw = p_regen_kw / 1000.0
            delta_e_mj = p_regen_mw * dt
            self.ers_energy_mj = min(self.ers_max_energy_mj, self.ers_energy_mj + delta_e_mj)
            self.ers_status = "REGEN"

            # Fuel flow cutoff under braking
            self.fuel_flow_kgh = 0.0
        else:
            aggression = getattr(self.driver, "aggression", 0.7)
            agg_mult = 0.85 + (aggression * 0.15)

            # High-downforce formula power delivery
            speed_ratio = min(1.0, self.speed_ms / max(1.0, self.max_speed_ms))
            power_factor = max(0.38, 1.0 - (0.42 * speed_ratio))

            if self.fuel <= 0.0:
                # Fuel starvation: ICE engine cannot produce torque
                base_engine_accel = 0.0
                self.fuel = 0.0
                self.fuel_flow_kgh = 0.0
            else:
                base_engine_accel = self.acceleration * agg_mult * power_factor * self.throttle * self.mass_factor

            # Hybrid Powertrain Deploy & Manual Override Mode (MOM)
            electric_accel_boost = 0.0
            if self.mom_active and self.ers_soc_pct >= 10.0:
                # MOM: Extra 350 kW electrical boost added to engine (a = P / (M * v))
                electric_accel_boost = 350_000.0 / (self.total_mass_kg * max(20.0, self.speed_ms))
                electric_accel_boost = min(6.0, max(2.5, electric_accel_boost))

                # Rapid battery depletion: 350 kW rate (0.35 MJ/s)
                deplete_mj = 0.350 * dt
                self.ers_energy_mj = max(0.0, self.ers_energy_mj - deplete_mj)
                self.ers_status = "MOM ACTIVE"

                # Automatic shutoff if battery drops below 10%
                if self.ers_soc_pct < 10.0:
                    self.mom_active = False
            elif is_straight and self.throttle > 0.5 and self.ers_soc_pct > 5.0:
                # Standard Hybrid Deploy: ~120 kW baseline assist
                electric_accel_boost = 1.4 * self.throttle * self.mass_factor
                deplete_mj = 0.120 * self.throttle * dt
                self.ers_energy_mj = max(0.0, self.ers_energy_mj - deplete_mj)
                self.ers_status = "DEPLOY"
            else:
                self.ers_status = "IDLE"

            net_accel = base_engine_accel + electric_accel_boost - a_drag

            # Top speed headroom: +5% in X-Mode (low drag), and +15% in MOM (full power override)
            speed_mult = 1.0
            if self.mom_active:
                speed_mult = 1.15
            elif self.aero_mode == "X-MODE":
                speed_mult = 1.05

            top_speed_cap = self.max_speed_ms * speed_mult
            if self.in_pit_lane:
                top_speed_cap = min(top_speed_cap, 80.0 / 3.6)
            self.speed_ms = max(0.0, min(top_speed_cap, self.speed_ms + net_accel * dt))

            # Fuel flow rate (kg/h) and deterministic mass consumption
            if self.fuel > 0.0:
                self.fuel_flow_kgh = self.throttle * 80.0
                fuel_burned_kg = (self.fuel_flow_kgh / 3600.0) * dt
                self.fuel = max(0.0, self.fuel - fuel_burned_kg)
            else:
                self.fuel = 0.0
                self.fuel_flow_kgh = 0.0

    def _update_transmission(self) -> None:
        """Determines active gear and calculates realistic engine RPM."""
        spd = self.speed  # km/h

        # 8-speed gearbox thresholds
        if spd < 70.0:
            self.gear = 1
            gear_min, gear_max = 0.0, 70.0
        elif spd < 110.0:
            self.gear = 2
            gear_min, gear_max = 70.0, 110.0
        elif spd < 150.0:
            self.gear = 3
            gear_min, gear_max = 110.0, 150.0
        elif spd < 190.0:
            self.gear = 4
            gear_min, gear_max = 150.0, 190.0
        elif spd < 230.0:
            self.gear = 5
            gear_min, gear_max = 190.0, 230.0
        elif spd < 270.0:
            self.gear = 6
            gear_min, gear_max = 230.0, 270.0
        elif spd < 305.0:
            self.gear = 7
            gear_min, gear_max = 270.0, 305.0
        else:
            self.gear = 8
            gear_min, gear_max = 305.0, 335.0

        # Engine RPM curve (4,500 idle/shift floor to 12,800 redline)
        fraction = max(0.0, min(1.0, (spd - gear_min) / max(1.0, gear_max - gear_min)))
        self.rpm = 4800.0 + (fraction * 7800.0)
