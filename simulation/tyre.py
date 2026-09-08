"""Physical 4-Wheel Dynamic Tyre Thermal and Wear Model.

Calculates independent temperatures, thermal grip degradation, and mechanical
wear for Front-Left, Front-Right, Rear-Left, and Rear-Right tyres based on
longitudinal braking forces, lateral cornering loads (with weight transfer),
engine acceleration, and convective airflow cooling.
"""

from dataclasses import dataclass
from enum import Enum


class CompoundType(Enum):
    """Formula 1 Tyre Compounds with distinct friction, thermal warmup, and wear kinetics."""

    SOFT = ("Soft", "S", "#FF334B", 1.85, 1.35, 1.75)
    MEDIUM = ("Medium", "M", "#FFD600", 1.70, 1.00, 1.00)
    HARD = ("Hard", "H", "#FFFFFF", 1.55, 0.70, 0.55)

    def __init__(
        self,
        compound_name: str,
        code: str,
        color: str,
        base_grip: float,
        warmup_rate: float,
        wear_rate: float,
    ):
        self.compound_name = compound_name
        self.code = code
        self.color = color
        self.base_grip = base_grip
        self.warmup_rate = warmup_rate
        self.wear_rate = wear_rate

    @classmethod
    def from_str(cls, val: str) -> "CompoundType":
        val_upper = str(val).upper().strip()
        if "SOFT" in val_upper or val_upper == "S":
            return cls.SOFT
        elif "HARD" in val_upper or val_upper == "H":
            return cls.HARD
        return cls.MEDIUM


@dataclass
class WheelState:
    """Represents the thermodynamic and mechanical status of a single wheel."""

    position: str  # "FL", "FR", "RL", "RR"
    temperature: float = 80.0  # Celsius (baseline/preheated operating temp)
    wear: float = 0.0  # 0.0 (fresh new) to 1.0 (100% bald/punctured)

    thermal_grip: float = 0.90
    wear_grip: float = 1.0
    effective_grip: float = 0.90

    def update_grip(self, base_grip_factor: float = 1.0) -> None:
        """Calculates grip coefficient based on thermal window, tyre wear, and base grip."""
        # 1. Thermal Grip Curve (Optimal peak: 95°C to 105°C)
        if 95.0 <= self.temperature <= 105.0:
            self.thermal_grip = 1.0
        elif self.temperature < 95.0:
            # Cold tyre fall-off: drops smoothly down to ~0.78 at 60°C
            delta = 95.0 - self.temperature
            self.thermal_grip = max(0.75, 1.0 - 0.22 * min(1.0, (delta / 30.0) ** 1.1))
        else:
            # Overheating degradation: drops down to ~0.72 at 125°C
            delta = self.temperature - 105.0
            self.thermal_grip = max(0.70, 1.0 - 0.28 * min(1.0, (delta / 25.0) ** 1.1))

        # 2. Wear Degradation Curve
        # Initial 0-20% wear has minimal loss; progressive drop thereafter
        clamped_wear = max(0.0, min(1.0, self.wear))
        self.wear_grip = max(0.65, 1.0 - 0.35 * (clamped_wear ** 1.35))

        self.effective_grip = base_grip_factor * self.thermal_grip * self.wear_grip


class TyreSet:
    """Manages the full four-wheel tyre assembly on a formula racing car."""

    def __init__(self, compound: CompoundType = CompoundType.MEDIUM, initial_temp: float = 80.0):
        self.compound: CompoundType = compound
        self.laps_on_set: int = 0
        self.wheels: dict[str, WheelState] = {
            "FL": WheelState("FL", temperature=initial_temp),
            "FR": WheelState("FR", temperature=initial_temp),
            "RL": WheelState("RL", temperature=initial_temp),
            "RR": WheelState("RR", temperature=initial_temp),
        }
        for w in self.wheels.values():
            w.update_grip(base_grip_factor=1.0)

    @property
    def fl(self) -> WheelState:
        return self.wheels["FL"]

    @property
    def fr(self) -> WheelState:
        return self.wheels["FR"]

    @property
    def rl(self) -> WheelState:
        return self.wheels["RL"]

    @property
    def rr(self) -> WheelState:
        return self.wheels["RR"]

    def get_average_temp(self) -> float:
        return sum(w.temperature for w in self.wheels.values()) / 4.0

    def get_average_wear(self) -> float:
        return sum(w.wear for w in self.wheels.values()) / 4.0

    def get_average_grip(self) -> float:
        """Returns normalized thermal and wear condition efficiency (0.0 to 1.0)."""
        return sum(w.effective_grip for w in self.wheels.values()) / 4.0

    def get_compound_grip(self) -> float:
        """Returns physical cornering grip factor scaled by compound friction (Soft 1.85, Med 1.70, Hard 1.55)."""
        # Baseline medium is 1.70
        relative_factor = self.compound.base_grip / 1.70
        return relative_factor * self.get_average_grip()

    def change_compound(self, new_compound: CompoundType, initial_temp: float = 80.0) -> None:
        """Fitted fresh set of tyres during a pit stop with tyre warmers at 80°C."""
        self.compound = new_compound
        self.laps_on_set = 0
        self.reset(initial_temp=initial_temp)

    def reset(self, initial_temp: float = 80.0) -> None:
        """Resets all tyres to fresh state and preheated blanket temperature."""
        for pos in ("FL", "FR", "RL", "RR"):
            self.wheels[pos].temperature = initial_temp
            self.wheels[pos].wear = 0.0
            self.wheels[pos].update_grip(base_grip_factor=1.0)

    def update(
        self,
        dt: float,
        speed_ms: float,
        brake: float,
        throttle: float,
        corner_radius: float | None,
        turn_direction: str = "straight",
        driver_tyre_mgmt: float = 0.85,
    ) -> None:
        """Performs thermodynamic and wear integration for dt seconds.

        Args:
            dt: Time step in seconds.
            speed_ms: Vehicle longitudinal speed in m/s.
            brake: Normalized braking application (0.0 to 1.0).
            throttle: Normalized throttle application (0.0 to 1.0).
            corner_radius: Radius of the current track curve in meters (None for straight).
            turn_direction: "left", "right", or "straight".
            driver_tyre_mgmt: Driver skill factor (0.0 to 1.0), reduces wear rate.
        """
        ambient_temp = 25.0

        # -------------------------------------------------------------
        # 1. BRAKING HEAT FLUX (Dominantly heats front tyres FL & FR)
        # -------------------------------------------------------------
        # Front weight transfer: 62% front axle, 38% rear axle
        k_brake = 3.20  # Heat generation coefficient °C/s at 100% brake and 200 km/h
        raw_brake_heat = k_brake * brake * (speed_ms / 40.0)

        brake_share = {
            "FL": 0.31,
            "FR": 0.31,
            "RL": 0.19,
            "RR": 0.19,
        }

        # -------------------------------------------------------------
        # 2. CORNERING / LATERAL LOAD HEAT FLUX (Weight transfer to outside)
        # -------------------------------------------------------------
        # In a left turn: Outside is RIGHT (FR, RR) -> receives ~78% lateral load
        # In a right turn: Outside is LEFT (FL, RL) -> receives ~78% lateral load
        corner_heat_rates = {"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0}
        lat_g = 0.0

        if corner_radius is not None and corner_radius > 10.0 and speed_ms > 5.0:
            a_lat = (speed_ms * speed_ms) / corner_radius
            lat_g = min(5.5, a_lat / 9.81)

            # High lateral-G generation rate
            k_lat = 2.45
            total_lat_heat = k_lat * (lat_g ** 1.3) * (speed_ms / 35.0)

            if turn_direction == "left":
                # Outside is Right (FR, RR); front steered tyre bears heavy scrub
                corner_heat_rates["FL"] = total_lat_heat * 0.10
                corner_heat_rates["FR"] = total_lat_heat * 0.44  # Heavy scrub
                corner_heat_rates["RL"] = total_lat_heat * 0.12
                corner_heat_rates["RR"] = total_lat_heat * 0.34
            elif turn_direction == "right":
                # Outside is Left (FL, RL)
                corner_heat_rates["FL"] = total_lat_heat * 0.44  # Heavy scrub
                corner_heat_rates["FR"] = total_lat_heat * 0.10
                corner_heat_rates["RL"] = total_lat_heat * 0.34
                corner_heat_rates["RR"] = total_lat_heat * 0.12
            else:
                corner_heat_rates["FL"] = total_lat_heat * 0.25
                corner_heat_rates["FR"] = total_lat_heat * 0.25
                corner_heat_rates["RL"] = total_lat_heat * 0.25
                corner_heat_rates["RR"] = total_lat_heat * 0.25

        # -------------------------------------------------------------
        # 3. ACCELERATION / TRACTION HEAT FLUX (Heats rear tyres RL & RR)
        # -------------------------------------------------------------
        k_accel = 1.60
        # Torque slip is highest at lower/mid speeds when accelerating hard
        torque_factor = max(0.20, 1.0 - (speed_ms / 95.0))
        total_accel_heat = k_accel * throttle * torque_factor

        accel_share = {
            "FL": 0.02,
            "FR": 0.02,
            "RL": 0.48,
            "RR": 0.48,
        }

        # -------------------------------------------------------------
        # 4. ROLLING RESISTANCE HEAT FLUX (Baseline heating at speed)
        # -------------------------------------------------------------
        k_rolling = 0.015 * (speed_ms / 30.0)

        # -------------------------------------------------------------
        # 5. CONVECTIVE AIRFLOW COOLING
        # -------------------------------------------------------------
        # Cooling rate increases with airspeed: Q_cool = (h_base + h_speed * v) * (T - T_amb)
        h_base = 0.006
        h_speed = 0.00018 * speed_ms

        # -------------------------------------------------------------
        # 6. DEGRADATION & WEAR INTEGRATION
        # -------------------------------------------------------------
        # Mechanical wear coefficient scaled for realistic 15-20 lap Grand Prix stint
        base_wear_rate = 0.000035

        wear_mult = getattr(self.compound, "wear_rate", 1.0)

        for pos, wheel in self.wheels.items():
            # Thermal warmup multiplier applies primarily while bringing cold tyres to operating window
            warmup_mult = getattr(self.compound, "warmup_rate", 1.0) if wheel.temperature < 100.0 else 1.0

            # Thermal heat inputs scaled by compound warmup rate
            q_in = (
                (raw_brake_heat * brake_share[pos])
                + corner_heat_rates[pos]
                + (total_accel_heat * accel_share[pos])
                + k_rolling
            ) * warmup_mult

            # Convective heat loss to ambient air
            temp_diff = max(0.0, wheel.temperature - ambient_temp)
            q_out = (h_base + h_speed) * temp_diff

            net_dt_temp = (q_in - q_out) * dt
            wheel.temperature = max(ambient_temp, min(145.0, wheel.temperature + net_dt_temp))

            # Wear accumulation scaled by compound wear rate
            pos_lat_load = corner_heat_rates[pos] / max(1.0, sum(corner_heat_rates.values()) if corner_radius else 1.0)
            lat_wear_component = (lat_g ** 1.6) * pos_lat_load * 3.2
            long_wear_component = (brake * brake_share[pos] * 2.2) + (throttle * accel_share[pos] * 1.8)

            # Temperature degradation penalty (blistering/graining if overheated)
            thermal_stress = 1.0
            if wheel.temperature > 105.0:
                thermal_stress += 0.035 * (wheel.temperature - 105.0)

            # Driver tyre management mitigation (higher skill = less wear)
            driver_factor = max(0.5, 1.30 - (driver_tyre_mgmt * 0.40))

            wear_increment = base_wear_rate * wear_mult * (1.0 + lat_wear_component + long_wear_component) * thermal_stress * driver_factor * dt
            wheel.wear = min(1.0, wheel.wear + wear_increment)

            wheel.update_grip(base_grip_factor=1.0)
