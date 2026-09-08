"""Race View-Model & Adapter Layer.

Decouples the UI from the simulation internals, processes telemetry snapshots,
computes dynamic standings, tracks timing, and maintains historical buffers
for live telemetry graphs.
"""

from collections import deque
from dataclasses import dataclass
from typing import Any

from simulation.race import Race
from simulation.telemetry import Telemetry


@dataclass
class DriverSnapshot:
    """Snapshot of a single driver's state for UI consumption."""
    index: int
    name: str
    number: int
    color: str

    # Current telemetry
    speed: float
    throttle: float
    brake: float
    gear: int
    rpm: float
    position_m: float
    sector: int

    # Circuit progression
    current_lap: int
    total_laps: int
    track_progress: float  # 0.0 to 1.0 along the circuit
    total_distance: float

    # Standings & timing
    position_rank: int
    gap_to_leader_s: float
    current_lap_time_s: float | None
    last_lap_time_s: float | None
    best_lap_time_s: float | None
    sector_times_s: dict[int, float | None]

    # Tyre and Fuel telemetry fields
    tyre_temperature: float
    tyre_wear: float
    fuel: float
    is_tyre_fuel_baseline: bool = False

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


@dataclass
class LeaderboardEntry:
    """Entry displayed in the race leaderboard."""
    rank: int
    driver_number: int
    driver_name: str
    driver_color: str
    lap_text: str
    gap_text: str
    sector: int
    speed_kmh: float
    is_selected: bool
    override_ready: bool = False

    # V0.6 Strategy fields
    compound_code: str = "M"
    compound_color: str = "#FFD600"
    laps_on_set: int = 0
    pit_stops: int = 0
    in_pit_lane: bool = False
    pit_state: str = "RACING"


class RaceViewModel:
    """Encapsulates race simulation state for UI widgets."""

    def __init__(self, race: Race):
        self._race = race
        self._elapsed_time: float = 0.0
        self._selected_driver_name: str = ""

        # Pre-assign driver colors
        self._driver_colors = [
            "#00E5FF",  # Cyan (Car A / #7)
            "#FF9F1C",  # Amber (Car B / #22)
            "#00E676",  # Fallback accents for future cars
            "#BD00FF",
        ]

        num_cars = len(race.cars)
        if num_cars > 0:
            self._selected_driver_name = race.cars[0].driver.name

        # Timing tracking per driver index
        self._lap_start_times: list[float] = [0.0] * num_cars
        self._last_lap_times: list[float | None] = [None] * num_cars
        self._best_lap_times: list[float | None] = [None] * num_cars
        self._prev_laps: list[int] = [0] * num_cars

        self._sector_start_times: list[float] = [0.0] * num_cars
        self._prev_sectors: list[int] = [1] * num_cars
        self._sector_times: list[dict[int, float | None]] = [
            {1: None, 2: None, 3: None} for _ in range(num_cars)
        ]

        # Telemetry history for real-time graphs (speed over time)
        # buffer size 300 points @ 20Hz = 15 seconds history window
        self._history_maxlen = 300
        self._speed_histories: dict[str, deque] = {
            car.driver.name: deque(maxlen=self._history_maxlen)
            for car in race.cars
        }
        self._time_history: deque = deque(maxlen=self._history_maxlen)

        # Cached latest snapshots
        self._latest_snapshots: dict[str, DriverSnapshot] = {}
        self._leaderboard_entries: list[LeaderboardEntry] = []

    @property
    def track(self) -> Any:
        return self._race.track

    @property
    def track_name(self) -> str:
        return self._race.track.name

    @property
    def track_length(self) -> float:
        return self._race.track.length

    @property
    def sector_lengths(self) -> tuple[float, float, float]:
        return self._race.track.sector_lengths

    @property
    def total_laps(self) -> int:
        return self._race.total_laps

    @property
    def elapsed_time(self) -> float:
        return self._elapsed_time

    @property
    def is_finished(self) -> bool:
        return self._race.is_finished()

    @property
    def selected_driver_name(self) -> str:
        return self._selected_driver_name

    def set_selected_driver(self, name: str) -> None:
        if name in self._latest_snapshots:
            self._selected_driver_name = name

    def get_selected_snapshot(self) -> DriverSnapshot | None:
        return self._latest_snapshots.get(self._selected_driver_name)

    def get_all_snapshots(self) -> list[DriverSnapshot]:
        return list(self._latest_snapshots.values())

    def get_leaderboard(self) -> list[LeaderboardEntry]:
        return self._leaderboard_entries

    @property
    def leaderboard_entries(self) -> list[LeaderboardEntry]:
        return self._leaderboard_entries

    def get_speed_history(self, driver_name: str) -> deque:
        return self._speed_histories.get(driver_name, deque())

    def get_car(self, driver_name: str):
        """Returns the Car instance associated with the driver name."""
        for car in self._race.cars:
            if car.driver.name == driver_name:
                return car
        return None

    def get_car_setup(self, driver_name: str) -> dict:
        """Retrieves setup dictionary for the specified driver's car."""
        car = self.get_car(driver_name)
        if car and hasattr(car, "get_setup_dict"):
            return car.get_setup_dict()
        return {}

    def apply_car_setup(self, driver_name: str, setup: dict) -> None:
        """Applies setup adjustments to the specified car."""
        car = self.get_car(driver_name)
        if car and hasattr(car, "apply_setup_dict"):
            car.apply_setup_dict(setup)

    def reset_car_setup(self, driver_name: str) -> None:
        """Resets the specified car to factory setup defaults."""
        car = self.get_car(driver_name)
        if car and hasattr(car, "reset_to_defaults"):
            car.reset_to_defaults()

    def tick(self, dt: float) -> None:
        """Executes a simulation step and updates view model snapshots."""
        raw_telemetries: list[Telemetry] = self._race.update(dt)
        self._elapsed_time += dt
        self._time_history.append(self._elapsed_time)

        # 1. Update timing and histories
        for idx, car in enumerate(self._race.cars):
            driver_name = car.driver.name
            current_lap_count = self._race.laps[idx]

            # Lap transition detection
            if current_lap_count > self._prev_laps[idx]:
                lap_duration = self._elapsed_time - self._lap_start_times[idx]
                self._last_lap_times[idx] = lap_duration
                best_lap = self._best_lap_times[idx]
                if best_lap is None or lap_duration < best_lap:
                    self._best_lap_times[idx] = lap_duration

                self._lap_start_times[idx] = self._elapsed_time
                self._prev_laps[idx] = current_lap_count
                # Reset sector times for new lap
                self._sector_times[idx] = {1: None, 2: None, 3: None}

            # Sector transition detection
            current_sector = self._race.track.get_sector(car.position)
            prev_sector = self._prev_sectors[idx]
            if current_sector != prev_sector:
                sec_duration = self._elapsed_time - self._sector_start_times[idx]
                self._sector_times[idx][prev_sector] = sec_duration
                self._sector_start_times[idx] = self._elapsed_time
                self._prev_sectors[idx] = current_sector

            # Record telemetry history
            self._speed_histories[driver_name].append(car.speed)

        # 2. Compute true standings based on total distance
        # total_distance = (laps * track_length) + car.position
        driver_rankings = []
        for idx, car in enumerate(self._race.cars):
            laps_done = self._race.laps[idx]
            total_dist = (laps_done * self._race.track.length) + car.position
            driver_rankings.append((idx, car, total_dist))

        # Sort descending by total distance
        driver_rankings.sort(key=lambda item: item[2], reverse=True)

        leader_total_dist = driver_rankings[0][2] if driver_rankings else 0.0

        # 3. Build snapshots
        new_snapshots: dict[str, DriverSnapshot] = {}
        new_leaderboard: list[LeaderboardEntry] = []

        for rank, (idx, car, total_dist) in enumerate(driver_rankings, start=1):
            driver = car.driver
            driver_name = driver.name
            current_lap = min(self._race.total_laps, self._race.laps[idx] + 1)
            track_prog = max(0.0, min(1.0, car.position / self._race.track.length))

            # Gap calculation to leader
            dist_delta = leader_total_dist - total_dist
            if rank == 1:
                gap_s = 0.0
                gap_text = "LEADER"
            else:
                # Speed in m/s: km/h / 3.6
                speed_ms = max(5.0, car.speed / 3.6)
                gap_s = dist_delta / speed_ms
                gap_text = f"+{gap_s:.3f}s"

            # Find matching raw telemetry
            raw_t: Telemetry | None = next(
                (t for t in raw_telemetries if t.driver == driver_name), None
            )

            tyre_temp = raw_t.tyre_temperature if raw_t else 80.0
            tyre_wear = raw_t.tyre_wear if raw_t else 0.0
            fuel_level = raw_t.fuel if raw_t else 100.0

            fl_t = getattr(raw_t, "fl_temp", tyre_temp) if raw_t else 80.0
            fr_t = getattr(raw_t, "fr_temp", tyre_temp) if raw_t else 80.0
            rl_t = getattr(raw_t, "rl_temp", tyre_temp) if raw_t else 80.0
            rr_t = getattr(raw_t, "rr_temp", tyre_temp) if raw_t else 80.0

            fl_w = getattr(raw_t, "fl_wear", tyre_wear) if raw_t else 0.0
            fr_w = getattr(raw_t, "fr_wear", tyre_wear) if raw_t else 0.0
            rl_w = getattr(raw_t, "rl_wear", tyre_wear) if raw_t else 0.0
            rr_w = getattr(raw_t, "rr_wear", tyre_wear) if raw_t else 0.0

            # 2026 Regulation fields
            aero_m = getattr(raw_t, "aero_mode", "Z-MODE") if raw_t else "Z-MODE"
            ers_soc = getattr(raw_t, "ers_soc_pct", 85.0) if raw_t else 85.0
            ers_mj = getattr(raw_t, "ers_energy_mj", 3.4) if raw_t else 3.4
            ers_st = getattr(raw_t, "ers_status", "IDLE") if raw_t else "IDLE"
            ovr_ready = getattr(raw_t, "override_ready", False) if raw_t else False
            f_flow = getattr(raw_t, "fuel_flow_kgh", 0.0) if raw_t else 0.0

            # Strategy, Tyre Compound & Pit Fields
            comp_name = getattr(raw_t, "compound", "Medium") if raw_t else "Medium"
            comp_code = getattr(raw_t, "compound_code", "M") if raw_t else "M"
            comp_color = getattr(raw_t, "compound_color", "#FFD600") if raw_t else "#FFD600"
            laps_on_set = getattr(raw_t, "laps_on_set", 0) if raw_t else 0
            pit_stops = getattr(raw_t, "pit_stops", 0) if raw_t else 0
            in_pit = getattr(raw_t, "in_pit_lane", False) if raw_t else False
            p_state = getattr(raw_t, "pit_state", "RACING") if raw_t else "RACING"

            color = self._driver_colors[idx % len(self._driver_colors)]

            cur_lap_time = self._elapsed_time - self._lap_start_times[idx]

            snapshot = DriverSnapshot(
                index=idx,
                name=driver_name,
                number=driver.number,
                color=color,
                speed=car.speed,
                throttle=car.throttle,
                brake=car.brake,
                gear=car.gear,
                rpm=car.rpm,
                position_m=car.position,
                sector=self._race.track.get_sector(car.position),
                current_lap=current_lap,
                total_laps=self._race.total_laps,
                track_progress=track_prog,
                total_distance=total_dist,
                position_rank=rank,
                gap_to_leader_s=gap_s,
                current_lap_time_s=cur_lap_time,
                last_lap_time_s=self._last_lap_times[idx],
                best_lap_time_s=self._best_lap_times[idx],
                sector_times_s=dict(self._sector_times[idx]),
                tyre_temperature=tyre_temp,
                tyre_wear=tyre_wear,
                fuel=fuel_level,
                is_tyre_fuel_baseline=False,
                fl_temp=fl_t,
                fr_temp=fr_t,
                rl_temp=rl_t,
                rr_temp=rr_t,
                fl_wear=fl_w,
                fr_wear=fr_w,
                rl_wear=rl_w,
                rr_wear=rr_w,
                aero_mode=aero_m,
                ers_soc_pct=ers_soc,
                ers_energy_mj=ers_mj,
                ers_status=ers_st,
                override_ready=ovr_ready,
                fuel_flow_kgh=f_flow,
                compound=comp_name,
                compound_code=comp_code,
                compound_color=comp_color,
                laps_on_set=laps_on_set,
                pit_stops=pit_stops,
                in_pit_lane=in_pit,
                pit_state=p_state,
            )

            new_snapshots[driver_name] = snapshot

            new_leaderboard.append(
                LeaderboardEntry(
                    rank=rank,
                    driver_number=driver.number,
                    driver_name=driver_name,
                    driver_color=color,
                    lap_text=f"LAP {current_lap:02d}",
                    gap_text=gap_text,
                    sector=snapshot.sector,
                    speed_kmh=car.speed,
                    is_selected=(driver_name == self._selected_driver_name),
                    override_ready=ovr_ready,
                    compound_code=comp_code,
                    compound_color=comp_color,
                    laps_on_set=laps_on_set,
                    pit_stops=pit_stops,
                    in_pit_lane=in_pit,
                    pit_state=p_state,
                )
            )

        self._latest_snapshots = new_snapshots
        self._leaderboard_entries = new_leaderboard

    def request_pit_stop(self, driver_name: str, next_compound: str | None = None) -> bool:
        """Manually commands a driver to box on the current lap with a chosen compound."""
        for car in self._race.cars:
            if car.driver.name == driver_name:
                car.pit_requested = True
                if next_compound:
                    from simulation.tyre import CompoundType
                    car.next_compound = CompoundType.from_str(next_compound)
                return True
        return False

    def set_track(self, new_track: Any) -> None:
        """Updates the circuit and resets timing states and lap buffers."""
        self._race.set_track(new_track)
        self._elapsed_time = 0.0
        num_cars = len(self._race.cars)
        self._prev_laps = [0] * num_cars
        self._lap_start_times = [0.0] * num_cars
        self._last_lap_times = [None] * num_cars
        self._best_lap_times = [None] * num_cars
        self._prev_sectors = [1] * num_cars
        self._sector_start_times = [0.0] * num_cars
        self._sector_times = [{1: None, 2: None, 3: None} for _ in range(num_cars)]
        self._time_history.clear()
        for d_name in self._speed_histories:
            self._speed_histories[d_name].clear()
