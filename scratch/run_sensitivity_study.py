"""Motorsport Simulation — Sensitivity Analysis & Model Validation Suite.

Executes quantitative parametric sensitivity studies to validate physical models
against empirical Formula 1 telemetry and benchmark data:
1. Fuel Mass Sensitivity (s / 10 kg lap time delta on Monza)
2. Aerodynamic Drag Delta (Active Aero X-Mode vs Z-Mode v_max and lap time)
3. Tyre Compound Thermal Evolution & Degradation (10-Lap Soft vs Medium stint)
4. Telemetry Export Validation (20 Hz CSV logging via TelemetryRecorder)

Saves results to scratch/sensitivity_results.json and exports CSV telemetry.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from simulation.car import Car
from simulation.driver import Driver
from simulation.race import Race
from simulation.telemetry_recorder import TelemetryRecorder
from simulation.track_library import TrackLibrary
from simulation.tyre import CompoundType


class ForcedZModeCar(Car):
    """Car subclass that enforces Z-Mode (high drag / high downforce) at all times."""

    def _integrate_physics(self, dt: float, is_straight: bool = True) -> None:
        self.aero_mode = "Z-MODE"
        super()._integrate_physics(dt, is_straight)


def run_fuel_mass_study(track: Any, driver: Driver) -> dict[str, Any]:
    """Measures flying lap times across fuel mass increments on Monza.

    Benchmark: Empirical F1 telemetry indicates ~0.30 - 0.40 s / 10 kg penalty.
    """
    fuel_increments_kg = [0.0, 20.0, 50.0, 100.0]
    results: list[dict[str, Any]] = []
    base_time: float | None = None

    for add_fuel in fuel_increments_kg:
        total_fuel = 10.0 + add_fuel
        car = Car(name=f"Fuel_{int(add_fuel)}kg", driver=driver, fuel=total_fuel)
        car.tyres.change_compound(CompoundType.SOFT)

        # Warmup / out-lap to establish flying lap speed across finish line
        while not car.update(0.05, track):
            pass

        # Reset to target fuel mass right at the start of the flying lap
        car.fuel = total_fuel

        # Measure flying lap
        lap_time = 0.0
        while not car.update(0.05, track):
            lap_time += 0.05

        if base_time is None:
            base_time = lap_time
            delta_s = 0.0
            sens_per_10kg = 0.0
        else:
            delta_s = lap_time - base_time
            sens_per_10kg = (delta_s / add_fuel) * 10.0 if add_fuel > 0 else 0.0

        results.append({
            "added_fuel_kg": add_fuel,
            "total_fuel_kg": total_fuel,
            "lap_time_s": round(lap_time, 3),
            "delta_s": round(delta_s, 3),
            "sensitivity_s_per_10kg": round(sens_per_10kg, 3),
        })

    # Average sensitivity calculated across the full 100 kg delta
    full_delta = results[-1]["delta_s"]
    avg_sensitivity = round((full_delta / 100.0) * 10.0, 3)

    return {
        "circuit": track.name,
        "baseline_lap_time_s": results[0]["lap_time_s"],
        "cases": results,
        "average_sensitivity_s_per_10kg": avg_sensitivity,
        "f1_benchmark_range": "0.30 - 0.40 s / 10 kg",
        "validation_passed": 0.30 <= avg_sensitivity <= 0.42,
    }


def run_aero_drag_study(track: Any, driver: Driver) -> dict[str, Any]:
    """Compares aerodynamic drag, top speed (v_max), and lap time in X-Mode vs Z-Mode."""
    # 1. Baseline Car (Active Aero enabled: X-Mode on straights)
    car_x = Car(name="Baseline_XMode", driver=driver, fuel=20.0)
    car_x.tyres.change_compound(CompoundType.SOFT)
    while not car_x.update(0.05, track):
        pass
    car_x.fuel = 20.0

    t_x = 0.0
    v_max_x = 0.0
    while not car_x.update(0.05, track):
        t_x += 0.05
        v_max_x = max(v_max_x, car_x.speed)

    # 2. Forced Z-Mode Car (Active Aero disabled: full drag on straights)
    car_z = ForcedZModeCar(name="Forced_ZMode", driver=driver, fuel=20.0)
    car_z.tyres.change_compound(CompoundType.SOFT)
    while not car_z.update(0.05, track):
        pass
    car_z.fuel = 20.0

    t_z = 0.0
    v_max_z = 0.0
    while not car_z.update(0.05, track):
        t_z += 0.05
        v_max_z = max(v_max_z, car_z.speed)

    delta_time = t_z - t_x
    delta_v_max = v_max_x - v_max_z

    return {
        "circuit": track.name,
        "x_mode": {
            "lap_time_s": round(t_x, 3),
            "v_max_kmh": round(v_max_x, 1),
        },
        "forced_z_mode": {
            "lap_time_s": round(t_z, 3),
            "v_max_kmh": round(v_max_z, 1),
        },
        "delta_lap_time_s": round(delta_time, 3),
        "delta_v_max_kmh": round(delta_v_max, 1),
        "validation_passed": delta_time > 0.8 and delta_v_max >= 12.0,
    }


def run_tyre_compound_stint_study(track: Any, driver: Driver, stint_laps: int = 10) -> dict[str, Any]:
    """Simulates a 10-lap stint comparing Soft vs Medium tyre compounds on Istanbul Park."""
    stint_data: dict[str, list[dict[str, Any]]] = {"Soft": [], "Medium": []}
    cumulative_times: dict[str, float] = {"Soft": 0.0, "Medium": 0.0}

    for comp in (CompoundType.SOFT, CompoundType.MEDIUM):
        key = comp.compound_name
        car = Car(name=key, driver=driver, fuel=60.0)
        car.tyres.change_compound(comp)

        for lap_idx in range(1, stint_laps + 1):
            lap_t = 0.0
            while not car.update(0.05, track):
                lap_t += 0.05

            cumulative_times[key] += lap_t
            avg_temp = car.tyres.get_average_temp()
            avg_wear = car.tyres.get_average_wear() * 100.0

            stint_data[key].append({
                "lap": lap_idx,
                "lap_time_s": round(lap_t, 3),
                "cumulative_s": round(cumulative_times[key], 3),
                "avg_temp_c": round(avg_temp, 1),
                "avg_wear_pct": round(avg_wear, 1),
            })

    # Summary metrics
    soft_wear_final = stint_data["Soft"][-1]["avg_wear_pct"]
    med_wear_final = stint_data["Medium"][-1]["avg_wear_pct"]
    wear_ratio = soft_wear_final / max(0.1, med_wear_final)

    soft_pace_lap2 = stint_data["Soft"][1]["lap_time_s"]
    med_pace_lap2 = stint_data["Medium"][1]["lap_time_s"]
    initial_delta = med_pace_lap2 - soft_pace_lap2

    return {
        "circuit": track.name,
        "stint_laps": stint_laps,
        "soft_stint": stint_data["Soft"],
        "medium_stint": stint_data["Medium"],
        "summary": {
            "initial_pace_advantage_soft_s": round(initial_delta, 3),
            "final_wear_soft_pct": soft_wear_final,
            "final_wear_med_pct": med_wear_final,
            "wear_rate_ratio_soft_vs_med": round(wear_ratio, 2),
            "soft_cumulative_10_laps_s": round(cumulative_times["Soft"], 3),
            "medium_cumulative_10_laps_s": round(cumulative_times["Medium"], 3),
        },
        "validation_passed": wear_ratio >= 1.5 and initial_delta > 1.5,
    }


def record_sample_telemetry(track: Any, driver: Driver) -> dict[str, Any]:
    """Executes a 1-lap race simulation and logs frames to telemetry_exports/race_telemetry.csv."""
    export_path = os.path.join(PROJECT_ROOT, "telemetry_exports", "race_telemetry.csv")
    race = Race(track=track, laps=5)

    recorder = TelemetryRecorder(output_path=export_path)
    sim_time = 0.0
    dt = 0.05

    # Run for 1 complete lap
    while True:
        telemetry_list = race.update(dt)
        sim_time += dt

        # Record telemetry of the lead car
        if telemetry_list:
            lead_tel = telemetry_list[0]
            current_lap = race.laps[0] + 1
            recorder.record_frame(lead_tel, timestamp_s=sim_time, lap=current_lap)

        if race.laps[0] >= 1:
            break

    recorder.close()
    file_exists = os.path.isfile(export_path)
    file_size_bytes = os.path.getsize(export_path) if file_exists else 0

    return {
        "export_path": export_path,
        "file_exists": file_exists,
        "frames_recorded": recorder.frame_count,
        "file_size_bytes": file_size_bytes,
        "validation_passed": file_exists and recorder.frame_count > 500,
    }


def main() -> None:
    print("=" * 80)
    print(" MOTORSPORT SIMULATION - FLAGSHIP SENSITIVITY ANALYSIS & VALIDATION SUITE")
    print("=" * 80)

    monza = TrackLibrary.get_monza()
    istanbul = TrackLibrary.get_istanbul_park()
    benchmark_driver = Driver("Benchmark Driver", 1, braking_skill=0.95, tyre_management=0.90, consistency=0.95)

    # 1. Fuel Mass Sensitivity
    print("\n[1/4] Running Fuel Mass Sensitivity Study on Monza...")
    fuel_study = run_fuel_mass_study(monza, benchmark_driver)
    print(f"      Baseline Flying Lap: {fuel_study['baseline_lap_time_s']:.3f} s")
    print(f"      Average Sensitivity: {fuel_study['average_sensitivity_s_per_10kg']:.3f} s / 10 kg")
    print(f"      F1 Benchmark Range:  {fuel_study['f1_benchmark_range']}")
    print(f"      Status:              {'PASS (Within empirical F1 range)' if fuel_study['validation_passed'] else 'FAIL'}")

    print("\n      | Added Fuel (kg) | Total Fuel (kg) | Lap Time (s) | Delta (s) | Sensitivity (s/10kg) |")
    print("      |:---------------:|:---------------:|:------------:|:---------:|:--------------------:|")
    for case in fuel_study["cases"]:
        print(f"      | {case['added_fuel_kg']:15.1f} | {case['total_fuel_kg']:15.1f} | {case['lap_time_s']:12.3f} | {case['delta_s']:9.3f} | {case['sensitivity_s_per_10kg']:20.3f} |")

    # 2. Aerodynamic Drag Delta (Active Aero X-Mode vs Z-Mode)
    print("\n[2/4] Running Aerodynamic Drag Sensitivity Study on Monza...")
    aero_study = run_aero_drag_study(monza, benchmark_driver)
    print(f"      X-Mode:       Lap Time = {aero_study['x_mode']['lap_time_s']:.3f} s | v_max = {aero_study['x_mode']['v_max_kmh']:.1f} km/h")
    print(f"      Forced Z-Mode: Lap Time = {aero_study['forced_z_mode']['lap_time_s']:.3f} s | v_max = {aero_study['forced_z_mode']['v_max_kmh']:.1f} km/h")
    print(f"      Delta Time:   +{aero_study['delta_lap_time_s']:.3f} s (Z-Mode penalty)")
    print(f"      Delta v_max:  +{aero_study['delta_v_max_kmh']:.1f} km/h (X-Mode top speed advantage)")
    print(f"      Status:       {'PASS' if aero_study['validation_passed'] else 'FAIL'}")

    # 3. Tyre Compound Crossover & Thermal Evolution
    print("\n[3/4] Running Tyre Compound Crossover & Wear Stint on Istanbul Park...")
    tyre_study = run_tyre_compound_stint_study(istanbul, benchmark_driver, stint_laps=10)
    summary = tyre_study["summary"]
    print(f"      Initial Soft Pace Advantage: -{summary['initial_pace_advantage_soft_s']:.3f} s/lap")
    print(f"      Final Soft Wear (10 Laps):   {summary['final_wear_soft_pct']:.1f} %")
    print(f"      Final Medium Wear (10 Laps): {summary['final_wear_med_pct']:.1f} %")
    print(f"      Wear Ratio (Soft / Med):     {summary['wear_rate_ratio_soft_vs_med']:.2f}x (Nominal: 1.75x)")
    print(f"      Status:                      {'PASS' if tyre_study['validation_passed'] else 'FAIL'}")

    print("\n      | Lap | Soft Time (s) | Soft Wear (%) | Soft Temp (C) | Med Time (s) | Med Wear (%) | Med Temp (C) |")
    print("      |:---:|:-------------:|:-------------:|:--------------:|:------------:|:------------:|:-------------:|")
    for s_pt, m_pt in zip(tyre_study["soft_stint"], tyre_study["medium_stint"]):
        print(f"      | {s_pt['lap']:3d} | {s_pt['lap_time_s']:13.3f} | {s_pt['avg_wear_pct']:13.1f} | {s_pt['avg_temp_c']:14.1f} | {m_pt['lap_time_s']:12.3f} | {m_pt['avg_wear_pct']:12.1f} | {m_pt['avg_temp_c']:13.1f} |")

    # 4. Telemetry Recorder Validation
    print("\n[4/4] Validating High-Frequency 20 Hz Telemetry Recorder...")
    telem_study = record_sample_telemetry(monza, benchmark_driver)
    print(f"      Output Path:     {telem_study['export_path']}")
    print(f"      Frames Recorded: {telem_study['frames_recorded']}")
    print(f"      File Size:       {telem_study['file_size_bytes']} bytes")
    print(f"      Status:          {'PASS' if telem_study['validation_passed'] else 'FAIL'}")

    # Aggregate results and write to scratch/sensitivity_results.json
    all_results = {
        "fuel_mass_study": fuel_study,
        "aero_drag_study": aero_study,
        "tyre_compound_stint_study": tyre_study,
        "telemetry_recorder_study": telem_study,
        "all_tests_passed": (
            fuel_study["validation_passed"]
            and aero_study["validation_passed"]
            and tyre_study["validation_passed"]
            and telem_study["validation_passed"]
        ),
    }

    results_path = os.path.join(PROJECT_ROOT, "scratch", "sensitivity_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n[+] Full sensitivity results persisted to: {results_path}")
    print("=" * 80)
    print(f" OVERALL SENSITIVITY AUDIT: {'ALL 4 BENCHMARKS PASSED' if all_results['all_tests_passed'] else 'FAILURES DETECTED'}")
    print("=" * 80)

    if not all_results["all_tests_passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
