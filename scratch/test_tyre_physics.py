"""Automated verification test for Dynamic Tyre Thermal Physics & Track Library.

Tests:
1. Intercity Istanbul Park Turn 8 Asymmetric Tyre Heating (FR/RR vs FL/RL).
2. Straight-line convective airflow cooling on the long back straight.
3. Driver tyre management mitigation on wear rates.
4. Multi-circuit simulation validation across Monza, Istanbul Park, Silverstone, Prototype.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulation.car import Car
from simulation.driver import Driver
from simulation.race import Race
from simulation.track import Track
from simulation.track_library import TrackLibrary


def test_istanbul_park_turn_8_asymmetry():
    print("=" * 80)
    print("TEST 1: INTERCITY ISTANBUL PARK — TURN 8 ASYMMETRIC TYRE HEATING TEST")
    print("=" * 80)

    track = TrackLibrary.get_istanbul_park()
    driver = Driver(
        name="Driver A",
        number=7,
        aggression=0.85,
        consistency=0.92,
        tyre_management=0.76,
        braking_skill=0.88,
    )
    car = Car(
        name="Car A",
        driver=driver,
        max_speed=325.0,
        acceleration=12.4,
    )

    dt = 0.05
    total_time = 0.0

    # Turn 8 boundaries: 2,470 m to 3,150 m
    # Segment: "Turn 8 Quad-Apex Sweeper", corner_radius=180m, direction="left"
    t8_entry_temps = {}
    t8_exit_temps = {}
    max_t8_temps = {"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0}
    back_straight_entry_temps = {}
    back_straight_exit_temps = {}

    laps_completed = 0
    while laps_completed < 1:
        pos = car.position % track.length

        # Before Turn 8 entry (~2,440m - 2,470m)
        if 2440.0 <= pos <= 2470.0 and not t8_entry_temps:
            t8_entry_temps = {
                "FL": car.tyres.fl.temperature,
                "FR": car.tyres.fr.temperature,
                "RL": car.tyres.rl.temperature,
                "RR": car.tyres.rr.temperature,
            }

        # Inside Turn 8 (2,470m to 3,150m)
        if 2470.0 <= pos <= 3150.0:
            for p in ("FL", "FR", "RL", "RR"):
                curr = getattr(car.tyres, p.lower()).temperature
                if curr > max_t8_temps[p]:
                    max_t8_temps[p] = curr

        # At Turn 8 exit (~3,150m - 3,180m)
        if 3150.0 <= pos <= 3180.0 and not t8_exit_temps:
            t8_exit_temps = {
                "FL": car.tyres.fl.temperature,
                "FR": car.tyres.fr.temperature,
                "RL": car.tyres.rl.temperature,
                "RR": car.tyres.rr.temperature,
            }

        # Long Back straight (3,550m to 4,738m)
        if 3560.0 <= pos <= 3600.0 and not back_straight_entry_temps:
            back_straight_entry_temps = {
                "FL": car.tyres.fl.temperature,
                "FR": car.tyres.fr.temperature,
                "RL": car.tyres.rl.temperature,
                "RR": car.tyres.rr.temperature,
            }

        if 4680.0 <= pos <= 4730.0 and not back_straight_exit_temps:
            back_straight_exit_temps = {
                "FL": car.tyres.fl.temperature,
                "FR": car.tyres.fr.temperature,
                "RL": car.tyres.rl.temperature,
                "RR": car.tyres.rr.temperature,
            }

        lap_done = car.update(dt, track)
        total_time += dt
        if lap_done:
            break

    print(f"Lap completed in {total_time:.3f} s.")
    print(f"\n[Turn 8 Entry (2,470m)] -> FL: {t8_entry_temps['FL']:.1f}°C | FR: {t8_entry_temps['FR']:.1f}°C | RL: {t8_entry_temps['RL']:.1f}°C | RR: {t8_entry_temps['RR']:.1f}°C")
    print(f"[Turn 8 PEAK (Apex)]   -> FL: {max_t8_temps['FL']:.1f}°C | FR: {max_t8_temps['FR']:.1f}°C | RL: {max_t8_temps['RL']:.1f}°C | RR: {max_t8_temps['RR']:.1f}°C")
    print(f"[Turn 8 Exit (2,400m)]  -> FL: {t8_exit_temps['FL']:.1f}°C | FR: {t8_exit_temps['FR']:.1f}°C | RL: {t8_exit_temps['RL']:.1f}°C | RR: {t8_exit_temps['RR']:.1f}°C")

    # Verify asymmetric loading: In a left turn, FR and RR are outside tyres
    fr_delta = max_t8_temps["FR"] - t8_entry_temps["FR"]
    fl_delta = max_t8_temps["FL"] - t8_entry_temps["FL"]
    rr_delta = max_t8_temps["RR"] - t8_entry_temps["RR"]
    rl_delta = max_t8_temps["RL"] - t8_entry_temps["RL"]

    print(f"\nThermal Rise in Turn 8:")
    print(f" -> Outside Steered Front (FR): +{fr_delta:.2f}°C")
    print(f" -> Inside Steered Front  (FL): +{fl_delta:.2f}°C")
    print(f" -> Outside Driven Rear   (RR): +{rr_delta:.2f}°C")
    print(f" -> Inside Driven Rear    (RL): +{rl_delta:.2f}°C")

    assert max_t8_temps["FR"] > max_t8_temps["FL"], "FR (outside) must heat significantly more than FL (inside) in Turn 8!"
    assert max_t8_temps["RR"] > max_t8_temps["RL"], "RR (outside) must heat more than RL (inside) in Turn 8!"
    assert fr_delta > fl_delta * 2.0, "FR heating rate must be more than double FL due to lateral weight transfer!"
    print(">>> VERIFICATION PASSED: Outside right tyres (FR/RR) absorb dominant lateral load in Turn 8!")

    # Verify straight-line cooling
    print(f"\n[Back Straight Entry (~2,800m)] -> Avg Temp: {sum(back_straight_entry_temps.values())/4:.1f}°C")
    print(f"[Back Straight Exit  (~3,980m)] -> Avg Temp: {sum(back_straight_exit_temps.values())/4:.1f}°C")
    avg_cool = (sum(back_straight_entry_temps.values())/4) - (sum(back_straight_exit_temps.values())/4)
    print(f" -> Convective Airflow Cooling along straight: {avg_cool:.2f}°C")
    assert avg_cool > 0.0, "Tyres must cool down along high-speed straight due to convective airflow!"
    print(">>> VERIFICATION PASSED: Convective cooling physically active on straights!")


def test_driver_tyre_management():
    print("\n" + "=" * 80)
    print("TEST 2: DRIVER TYRE MANAGEMENT IMPACT ON DEGRADATION")
    print("=" * 80)

    track = TrackLibrary.get_monza()
    driver_smooth = Driver(name="Smooth Driver", number=1, tyre_management=0.95, aggression=0.70)
    driver_aggressive = Driver(name="Aggressive Driver", number=2, tyre_management=0.60, aggression=0.90)

    car_smooth = Car(name="Car 1", driver=driver_smooth)
    car_agg = Car(name="Car 2", driver=driver_aggressive)

    race = Race(track=track, laps=3)
    race.drivers = [driver_smooth, driver_aggressive]
    race.cars = [car_smooth, car_agg]

    dt = 0.05
    for _ in range(int(100.0 / dt)):  # Run ~100s
        race.update(dt)

    wear_smooth = car_smooth.tyres.get_average_wear() * 100.0
    wear_agg = car_agg.tyres.get_average_wear() * 100.0

    print(f"Smooth Driver (tyre_mgmt=0.95) Wear after stint: {wear_smooth:.4f}%")
    print(f"Aggressive Driver (tyre_mgmt=0.60) Wear after stint: {wear_agg:.4f}%")
    print(f"Wear Ratio: Aggressive wore {wear_agg / max(1e-5, wear_smooth):.2f}x faster than Smooth!")
    assert wear_agg > wear_smooth, "Aggressive driver with low tyre management must incur higher wear!"
    print(">>> VERIFICATION PASSED: Driver tyre management mitigation verified!")


def test_all_circuits_simulation():
    print("\n" + "=" * 80)
    print("TEST 3: ALL TRACKS IN TRACK LIBRARY SIMULATION VALIDATION")
    print("=" * 80)

    track_keys = ["monza", "istanbul", "silverstone", "prototype"]
    for key in track_keys:
        track = TrackLibrary.get_track(key)
        print(f"\nTesting Circuit: {track.name} (Length: {track.length:,.0f} m, Segments: {len(track.segments)})")
        assert len(track.segments) >= 10, f"{track.name} must have at least 10 segments!"
        assert len(track.waypoints) >= 10, f"{track.name} must have waypoints for 2D visual layout!"

        driver = Driver(name="Test Driver", number=7)
        car = Car(name="Test Car", driver=driver)

        dt = 0.05
        t = 0.0
        laps = 0
        while laps < 1 and t < 180.0:
            lap_done = car.update(dt, track)
            t += dt
            if lap_done:
                laps += 1
                break

        print(f" -> 1 Full Lap Completed in {t:.3f} s. Final Speed: {car.speed:.1f} km/h. Tyre Temp: {car.tyres.get_average_temp():.1f}°C")
        assert laps == 1, f"Failed to complete full lap on {track.name}"

    print("\n>>> VERIFICATION PASSED: All 4 circuits simulate and complete laps successfully!")


if __name__ == "__main__":
    test_istanbul_park_turn_8_asymmetry()
    test_driver_tyre_management()
    test_all_circuits_simulation()
    print("\n" + "=" * 80)
    print("ALL TYRE THERMAL & TRACK LIBRARY TESTS PASSED!")
    print("=" * 80)
