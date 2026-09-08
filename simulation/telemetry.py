from dataclasses import dataclass


@dataclass
class Telemetry:
    driver: str

    speed: float
    throttle: float
    brake: float

    gear: int
    rpm: float

    position: float
    sector: int

    tyre_temperature: float = 80.0
    tyre_wear: float = 0.0
    fuel: float = 100.0

    # Dynamic 4-wheel independent tyre telemetry
    fl_temp: float = 80.0
    fr_temp: float = 80.0
    rl_temp: float = 80.0
    rr_temp: float = 80.0
    fl_wear: float = 0.0
    fr_wear: float = 0.0
    rl_wear: float = 0.0
    rr_wear: float = 0.0

    # 2026 Regulations: Active Aero, ERS 4.0 MJ, and MOM Boost
    aero_mode: str = "Z-MODE"
    ers_soc_pct: float = 85.0
    ers_energy_mj: float = 3.4
    ers_status: str = "IDLE"
    override_ready: bool = False
    fuel_flow_kgh: float = 0.0

    # V0.6 Strategy, Dynamic Pit Stop & Tyre Compound Engine
    compound: str = "Medium"
    compound_code: str = "M"
    compound_color: str = "#FFD600"
    laps_on_set: int = 0
    pit_stops: int = 0
    in_pit_lane: bool = False
    pit_state: str = "RACING"
