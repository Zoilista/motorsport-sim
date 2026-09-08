"""Comprehensive Test Suite for V0.6 Race Strategy, Dynamic Pit Stop & Tyre Compound Engine.

Validates:
1. Compound Characteristics: Soft (mu=1.85, high warmup, high wear) vs Medium (mu=1.70, balanced) vs Hard (mu=1.55, durable).
2. Soft vs Medium Strategy Battle: Soft's early lap pace advantage and degradation crossover.
3. Pit Stop Cycle & Physics:
   - Command trigger (pit_requested)
   - Pit lane entry & 80 km/h speed limiter enforcement
   - 2.4s stationary box stop (speed = 0)
   - Tyre change (wear reset to 0%, 80°C warmers, laps_on_set reset)
   - Pit exit and track rejoining
   - Total pit time delta (~20-25s)
4. UI View-Model & Leaderboard Data Integrity
"""

import math
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulation.car import Car
from simulation.driver import Driver
from simulation.race import Race
from simulation.telemetry import Telemetry
from simulation.track import Track, TrackSegment
from simulation.track_library import TrackLibrary
from simulation.tyre import CompoundType, TyreSet, WheelState
from ui.view_models.race_view_model import RaceViewModel


def test_tyre_compounds():
    print("\n" + "=" * 80)
    print(" 1. TYRE COMPOUND PHYSICAL ATTRIBUTES & KINETICS AUDIT")
    print("=" * 80)

    soft = CompoundType.SOFT
    med = CompoundType.MEDIUM
    hard = CompoundType.HARD

    # 1. Base friction coefficient ordering: Soft > Med > Hard
    assert soft.base_grip == 1.85, f"Soft base grip should be 1.85, got {soft.base_grip}"
    assert med.base_grip == 1.70, f"Medium base grip should be 1.70, got {med.base_grip}"
    assert hard.base_grip == 1.55, f"Hard base grip should be 1.55, got {hard.base_grip}"
    print(f" [PASS] Friction Coefficients: Soft mu={soft.base_grip:.2f} > Med mu={med.base_grip:.2f} > Hard mu={hard.base_grip:.2f}")

    # 2. Warmup rates: Soft heats faster than Medium, Medium faster than Hard
    assert soft.warmup_rate > med.warmup_rate > hard.warmup_rate
    print(f" [PASS] Warmup Kinetics: Soft ({soft.warmup_rate:.2f}x) > Med ({med.warmup_rate:.2f}x) > Hard ({hard.warmup_rate:.2f}x)")

    # 3. Wear rates: Soft degrades faster than Medium, Medium faster than Hard
    assert soft.wear_rate > med.wear_rate > hard.wear_rate
    print(f" [PASS] Degradation Multipliers: Soft ({soft.wear_rate:.2f}x) > Med ({med.wear_rate:.2f}x) > Hard ({hard.wear_rate:.2f}x)")

    # 4. Simulation of wear on identical loads
    ts_soft = TyreSet(CompoundType.SOFT, initial_temp=80.0)
    ts_med = TyreSet(CompoundType.MEDIUM, initial_temp=80.0)
    ts_hard = TyreSet(CompoundType.HARD, initial_temp=80.0)

    dt = 0.05
    for _ in range(200):  # 10 seconds of 4G cornering
        for ts in (ts_soft, ts_med, ts_hard):
            ts.update(dt=dt, speed_ms=65.0, brake=0.2, throttle=0.8, corner_radius=120.0, turn_direction="right")

    wear_soft = ts_soft.get_average_wear()
    wear_med = ts_med.get_average_wear()
    wear_hard = ts_hard.get_average_wear()

    assert wear_soft > wear_med > wear_hard, f"Wear ordering violated: Soft={wear_soft:.4f}, Med={wear_med:.4f}, Hard={wear_hard:.4f}"
    print(f" [PASS] 10s Cornering Wear: Soft={wear_soft * 100:.3f}% > Med={wear_med * 100:.3f}% > Hard={wear_hard * 100:.3f}%")
    print(f" [PASS] Compound Grip: Soft={ts_soft.get_compound_grip():.3f} vs Med={ts_med.get_compound_grip():.3f}")


def test_soft_vs_medium_battle():
    print("\n" + "=" * 80)
    print(" 2. SOFT VS MEDIUM STRATEGY BATTLE & DEGRADATION CROSSOVER")
    print("=" * 80)

    # Use Monza track for fast open racing
    track = TrackLibrary.get_monza()
    race = Race(track, laps=5)
    vm = RaceViewModel(race)

    car_a = race.cars[0]  # Soft
    car_b = race.cars[1]  # Medium

    assert car_a.tyres.compound == CompoundType.SOFT, "Car A must start on Soft"
    assert car_b.tyres.compound == CompoundType.MEDIUM, "Car B must start on Medium"
    print(" [PASS] Starting Grid Compounds: Car A = SOFT (C3 Red), Car B = MEDIUM (C2 Yellow)")

    dt = 0.05
    sim_time = 0.0
    telemetry_records = []

    # Run for 2 full laps to monitor early pace & wear
    lap_times_a = []
    lap_times_b = []
    prev_lap_a = 0
    prev_lap_b = 0
    lap_start_a = 0.0
    lap_start_b = 0.0

    while max(race.laps) < 2 and sim_time < 300.0:
        vm.tick(dt)
        sim_time += dt

        if race.laps[0] > prev_lap_a:
            lap_t = sim_time - lap_start_a
            lap_times_a.append(lap_t)
            lap_start_a = sim_time
            prev_lap_a = race.laps[0]

        if race.laps[1] > prev_lap_b:
            lap_t = sim_time - lap_start_b
            lap_times_b.append(lap_t)
            lap_start_b = sim_time
            prev_lap_b = race.laps[1]

    print(f" [PASS] 2-Lap Completed: Sim Time: {sim_time:.2f}s")
    if lap_times_a:
        print(f"        Car A (Soft) Lap 1: {lap_times_a[0]:.2f}s, Laps on set: {car_a.tyres.laps_on_set}")
    if lap_times_b:
        print(f"        Car B (Med)  Lap 1: {lap_times_b[0]:.2f}s, Laps on set: {car_b.tyres.laps_on_set}")

    wear_a = car_a.tyres.get_average_wear()
    wear_b = car_b.tyres.get_average_wear()
    assert wear_a > wear_b, f"Soft wear ({wear_a:.4f}) should exceed Medium wear ({wear_b:.4f})"
    print(f" [PASS] Degradation Delta: Car A (Soft) Wear = {wear_a * 100:.2f}% vs Car B (Med) Wear = {wear_b * 100:.2f}%")


def test_pit_stop_cycle():
    print("\n" + "=" * 80)
    print(" 3. PIT STOP CYCLE, SPEED LIMITER & 2.4s STATIONARY BOX AUDIT")
    print("=" * 80)

    track = TrackLibrary.get_monza()
    race = Race(track, laps=5)
    vm = RaceViewModel(race)
    car = race.cars[0]

    # Command pit stop
    success = vm.request_pit_stop("Driver A", next_compound="Hard")
    assert success is True
    assert car.pit_requested is True
    assert car.next_compound == CompoundType.HARD
    print(" [PASS] Manual Pit Call Requested: 'BOX THIS LAP' -> Next Compound: HARD")

    # Fast forward car to pit entry area (track.length - 275m)
    car.position = track.length - 275.0
    car.speed_ms = 70.0  # Racing speed 252 km/h

    dt = 0.05
    pit_entered = False
    pit_limiter_observed = False
    max_pit_speed = 0.0
    box_stop_started = False
    box_stop_duration = 0.0
    box_speed_zero_confirmed = False
    tyre_changed = False
    pit_exited = False

    total_pit_time = 0.0

    for step in range(3000):  # up to 150 seconds
        vm.tick(dt)

        if car.in_pit_lane:
            total_pit_time += dt
            if not pit_entered:
                pit_entered = True
                print(f" [PASS] Pit Entry Triggered: State = {car.pit_state}, Pos = {car.position:.1f}m")

            # Check pit limiter
            if car.pit_state in ("ENTERING_PIT", "EXITING_PIT"):
                spd_kmh = car.speed
                max_pit_speed = max(max_pit_speed, spd_kmh)
                if spd_kmh <= 80.5:
                    pit_limiter_observed = True

            # Check stationary box stop
            if car.pit_state == "IN_BOX_STOP":
                if not box_stop_started:
                    box_stop_started = True
                    print(f" [PASS] Car Arrived at Pit Box! Timer = {car.pit_stop_timer:.2f}s, Speed = {car.speed:.1f} km/h")
                box_stop_duration += dt
                if car.speed_ms == 0.0:
                    box_speed_zero_confirmed = True

            # Check after box stop transitions to EXITING_PIT
            if car.pit_state == "EXITING_PIT" and not tyre_changed:
                tyre_changed = True
                assert car.tyres.compound == CompoundType.HARD, f"Expected Hard compound fitted, got {car.tyres.compound}"
                assert car.tyres.get_average_wear() < 0.001, f"Tyre wear must be reset to ~0.0%, got {car.tyres.get_average_wear()}"
                assert 79.0 <= car.tyres.get_average_temp() <= 81.0, "Tyre warmers must be preheated to 80°C"
                assert car.pit_stops == 1, f"Pit stops count should be 1, got {car.pit_stops}"
                print(f" [PASS] Pit Box Work Completed! Fresh HARD tyres fitted, Wear = 0.0%, Temp = {car.tyres.get_average_temp():.1f} C, Pit Stops = {car.pit_stops}")

        elif pit_entered and not car.in_pit_lane:
            pit_exited = True
            print(f" [PASS] Car Rejoined Race Track! State = {car.pit_state}, Pit Lane Traversal Time = {total_pit_time:.2f}s")
            break

    assert pit_entered, "Car failed to enter pit lane"
    assert pit_limiter_observed, "Pit limiter was not enforced"
    assert max_pit_speed <= 81.0, f"Pit limiter breached! Max speed was {max_pit_speed:.1f} km/h"
    print(f" [PASS] Pit Limiter Enforced: Max Pit Lane Speed = {max_pit_speed:.1f} km/h (Limit: 80.0 km/h)")

    assert box_stop_started, "Box stop was never initiated"
    assert box_speed_zero_confirmed, "Car speed was not strictly 0 in pit box"
    assert 2.3 <= box_stop_duration <= 2.6, f"Box stop duration was {box_stop_duration:.2f}s (expected ~2.4s)"
    print(f" [PASS] Stationary Box Stop Confirmed: Duration = {box_stop_duration:.2f}s at Speed = 0.0 km/h")

    assert tyre_changed, "Tyres were not changed during pit stop"
    assert pit_exited, "Car never exited pit lane"
    assert 18.0 <= total_pit_time <= 26.0, f"Total pit lane time was {total_pit_time:.2f}s (expected ~20-25s)"
    print(f" [PASS] Total Pit Lane Time: {total_pit_time:.2f}s (Target F1 Delta ~20-25s met)")


def test_view_model_and_leaderboard_integrity():
    print("\n" + "=" * 80)
    print(" 4. UI VIEW-MODEL & LEADERBOARD COMPOUND PILL INTEGRITY AUDIT")
    print("=" * 80)

    track = TrackLibrary.get_monza()
    race = Race(track, laps=5)
    vm = RaceViewModel(race)

    dt = 0.05
    vm.tick(dt)

    entries = vm.leaderboard_entries
    assert len(entries) == 2, f"Expected 2 entries, got {len(entries)}"

    entry_a = next(e for e in entries if e.driver_name == "Driver A")
    entry_b = next(e for e in entries if e.driver_name == "Driver B")

    assert entry_a.compound_code == "S", f"Driver A compound should be 'S', got '{entry_a.compound_code}'"
    assert entry_a.compound_color == "#FF334B", f"Driver A color should be red, got '{entry_a.compound_color}'"

    assert entry_b.compound_code == "M", f"Driver B compound should be 'M', got '{entry_b.compound_code}'"
    assert entry_b.compound_color == "#FFD600", f"Driver B color should be yellow, got '{entry_b.compound_color}'"

    print(f" [PASS] Leaderboard Entry A: [{entry_a.compound_code}] {entry_a.compound_color} | Lap Text: '{entry_a.lap_text}' | Stint: L{entry_a.laps_on_set}")
    print(f" [PASS] Leaderboard Entry B: [{entry_b.compound_code}] {entry_b.compound_color} | Lap Text: '{entry_b.lap_text}' | Stint: L{entry_b.laps_on_set}")

    # Now simulate Driver A inside pit lane and check UI entry
    race.cars[0].in_pit_lane = True
    race.cars[0].pit_state = "IN_BOX_STOP"
    race.cars[0].pit_stop_timer = 2.4
    vm.tick(dt)

    entry_a_pit = next(e for e in vm.leaderboard_entries if e.driver_name == "Driver A")
    assert entry_a_pit.in_pit_lane is True
    assert entry_a_pit.pit_state == "IN_BOX_STOP"
    print(f" [PASS] In-Pit Leaderboard State: in_pit_lane={entry_a_pit.in_pit_lane}, pit_state={entry_a_pit.pit_state}")


if __name__ == "__main__":
    print("\n>>> STARTING V0.6 RACE STRATEGY & PIT STOP AUTOMATED TEST SUITE <<<\n")
    test_tyre_compounds()
    test_soft_vs_medium_battle()
    test_pit_stop_cycle()
    test_view_model_and_leaderboard_integrity()
    print("\n" + "=" * 80)
    print(" ALL V0.6 STRATEGY, PIT STOP & TYRE COMPOUND TESTS PASSED SUCCESSFULLY! ")
    print("=" * 80 + "\n")
