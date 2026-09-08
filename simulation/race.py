from .car import Car
from .driver import Driver
from .telemetry import Telemetry
from .track import Track
from .tyre import CompoundType


class Race:
    def __init__(self, track: Track, laps: int = 10):
        self.track = track
        self.total_laps = laps

        self.drivers = [
            Driver(
                name="Driver A",
                number=7,
                aggression=0.82,
                consistency=0.91,
                tyre_management=0.76,
                braking_skill=0.88,
            ),
            Driver(
                name="Driver B",
                number=22,
                aggression=0.68,
                consistency=0.96,
                tyre_management=0.89,
                braking_skill=0.81,
            ),
        ]

        self.cars = [
            Car(
                name="Car A",
                driver=self.drivers[0],
                max_speed=318,
                acceleration=12.4,
            ),
            Car(
                name="Car B",
                driver=self.drivers[1],
                max_speed=315,
                acceleration=12.1,
            ),
        ]

        # Initial strategy: Driver A on Soft (Sprint/Attack), Driver B on Medium (Endurance)
        self.cars[0].tyres.compound = CompoundType.SOFT
        self.cars[0].tyres.reset(initial_temp=80.0)
        self.cars[0].next_compound = CompoundType.MEDIUM

        self.cars[1].tyres.compound = CompoundType.MEDIUM
        self.cars[1].tyres.reset(initial_temp=80.0)
        self.cars[1].next_compound = CompoundType.HARD

        self.laps = [0, 0]

    def update(self, dt: float):
        telemetry = []
        track_len = self.track.length

        # 1. Multi-Car Aerodynamic Wake, Slipstream, and MOM Trigger Evaluation
        for i, car_i in enumerate(self.cars):
            # Identify the closest car ahead along the circuit
            closest_dist = float("inf")
            ahead_car = None

            for j, car_j in enumerate(self.cars):
                if i == j:
                    continue
                # Forward track distance from car_i to car_j
                gap_m = (car_j.position - car_i.position) % track_len
                if 0.5 <= gap_m < (track_len * 0.5) and gap_m < closest_dist:
                    closest_dist = gap_m
                    ahead_car = car_j

            if ahead_car is not None and closest_dist <= 65.0:
                seg_i = self.track.get_segment(car_i.position) if hasattr(self.track, "get_segment") else None
                seg_ahead = self.track.get_segment(ahead_car.position) if hasattr(self.track, "get_segment") else None
                same_segment = (seg_i is not None and seg_ahead is not None and seg_i.name == seg_ahead.name)
                is_straight = (seg_i.type == "straight") if seg_i is not None else True
                is_corner = (seg_i.type == "corner") if seg_i is not None else False

                # Time delta to car ahead (s)
                v_ms = max(5.0, car_i.speed_ms)
                time_delta_s = closest_dist / v_ms

                # Rule 1: Slipstream / Wake on straights
                if same_segment and is_straight and closest_dist >= 1.0:
                    # Linear reduction: 35% at 1.0m to 15% at 65.0m
                    fraction = (closest_dist - 1.0) / (65.0 - 1.0)
                    reduction = 0.35 - (fraction * (0.35 - 0.15))
                    car_i.slipstream_reduction = max(0.15, min(0.35, reduction))
                else:
                    car_i.slipstream_reduction = 0.0

                # Rule 2: Dirty Air in corners
                if is_corner and closest_dist >= 1.0:
                    car_i.in_dirty_air = True
                else:
                    car_i.in_dirty_air = False

                # Rule 3: Manual Override Mode (MOM) Detection (gap <= 1.0s, straight, speed >= 280 km/h)
                if is_straight and time_delta_s <= 1.0 and car_i.speed >= 280.0:
                    car_i.override_ready = True
                    # Driver AI activates MOM when override is ready and battery is sufficient
                    if car_i.ers_soc_pct >= 10.0 and car_i.throttle > 0.90 and car_i.brake <= 0.01:
                        car_i.mom_active = True
                else:
                    car_i.override_ready = False
            else:
                car_i.slipstream_reduction = 0.0
                car_i.in_dirty_air = False
                car_i.override_ready = False

        # 2. Vehicle Updates & Telemetry Gathering
        for index, car in enumerate(self.cars):
            completed_lap = car.update(
                dt,
                self.track
            )

            if completed_lap:
                self.laps[index] += 1
                if hasattr(car, "tyres") and car.tyres:
                    car.tyres.laps_on_set += 1

            # AI Strategy Decision Engine: Trigger pit stop when wear > 55%
            if (
                hasattr(car, "tyres")
                and car.tyres
                and car.tyres.get_average_wear() > 0.55
                and not car.in_pit_lane
                and not car.pit_requested
            ):
                car.pit_requested = True
                if car.tyres.compound == CompoundType.SOFT:
                    car.next_compound = CompoundType.MEDIUM
                elif car.tyres.compound == CompoundType.MEDIUM:
                    car.next_compound = CompoundType.HARD
                else:
                    car.next_compound = CompoundType.SOFT

            fl_t = car.tyres.fl.temperature if hasattr(car, "tyres") else 80.0
            fr_t = car.tyres.fr.temperature if hasattr(car, "tyres") else 80.0
            rl_t = car.tyres.rl.temperature if hasattr(car, "tyres") else 80.0
            rr_t = car.tyres.rr.temperature if hasattr(car, "tyres") else 80.0

            fl_w = car.tyres.fl.wear if hasattr(car, "tyres") else 0.0
            fr_w = car.tyres.fr.wear if hasattr(car, "tyres") else 0.0
            rl_w = car.tyres.rl.wear if hasattr(car, "tyres") else 0.0
            rr_w = car.tyres.rr.wear if hasattr(car, "tyres") else 0.0

            avg_temp = (fl_t + fr_t + rl_t + rr_t) / 4.0
            avg_wear = (fl_w + fr_w + rl_w + rr_w) / 4.0

            comp_name = car.tyres.compound.compound_name if hasattr(car, "tyres") else "Medium"
            comp_code = car.tyres.compound.code if hasattr(car, "tyres") else "M"
            comp_color = car.tyres.compound.color if hasattr(car, "tyres") else "#FFD600"
            laps_on_set = car.tyres.laps_on_set if hasattr(car, "tyres") else 0

            telemetry.append(
                Telemetry(
                    driver=car.driver.name,
                    speed=car.speed,
                    throttle=car.throttle,
                    brake=car.brake,
                    gear=car.gear,
                    rpm=car.rpm,
                    position=car.position,
                    sector=self.track.get_sector(car.position),
                    tyre_temperature=avg_temp,
                    tyre_wear=avg_wear,
                    fuel=car.fuel,
                    fl_temp=fl_t,
                    fr_temp=fr_t,
                    rl_temp=rl_t,
                    rr_temp=rr_t,
                    fl_wear=fl_w,
                    fr_wear=fr_w,
                    rl_wear=rl_w,
                    rr_wear=rr_w,
                    aero_mode=car.aero_mode,
                    ers_soc_pct=car.ers_soc_pct,
                    ers_energy_mj=car.ers_energy_mj,
                    ers_status=car.ers_status,
                    override_ready=car.override_ready,
                    fuel_flow_kgh=car.fuel_flow_kgh,
                    compound=comp_name,
                    compound_code=comp_code,
                    compound_color=comp_color,
                    laps_on_set=laps_on_set,
                    pit_stops=car.pit_stops,
                    in_pit_lane=car.in_pit_lane,
                    pit_state=car.pit_state,
                )
            )

        return telemetry

    def set_track(self, new_track: Track):
        """Switches the race to a new circuit and resets vehicle positions and tyres."""
        self.track = new_track
        self.laps = [0] * len(self.cars)
        for i, car in enumerate(self.cars):
            if hasattr(car, "reset_race_state"):
                car.reset_race_state()
            if hasattr(car, "tyres") and car.tyres:
                init_comp = CompoundType.SOFT if i == 0 else CompoundType.MEDIUM
                car.tyres.change_compound(init_comp, initial_temp=80.0)
                car.next_compound = CompoundType.MEDIUM if i == 0 else CompoundType.HARD

    def is_finished(self):
        return max(self.laps) >= self.total_laps
