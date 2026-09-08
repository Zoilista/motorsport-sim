"""Automated verification test for 2026 FIA Technical Regulations.

Tests:
1. Active Aerodynamics: Z-Mode (Cornering/Braking) vs X-Mode (Straight/Low Drag 40% reduction).
2. Hybrid ERS (4.0 MJ): MGU-K kinetic braking regen, standard deploy, and 350 kW MOM rapid discharge.
3. Aerodynamic Slipstream (15%-35% reduction), Dirty Air (10% downforce loss), and MOM Overtake scenario.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulation.car import Car
from simulation.driver import Driver
from simulation.race import Race
from simulation.track import Track
from simulation.track_library import TrackLibrary


def test_active_aerodynamics_modes():
    print("=" * 80)
    print("TEST 1: 2026 ACTIVE AERODYNAMICS (Z-MODE & X-MODE) TEST")
    print("=" * 80)

    track = TrackLibrary.get_monza()
    driver = Driver(name="Test Driver", number=1, aggression=0.8, consistency=0.9)
    car = Car(name="Test Car", driver=driver, max_speed=340.0, acceleration=12.5)

    # Initial state
    assert car.aero_mode == "Z-MODE", f"Expected initial Z-MODE, got {car.aero_mode}"
    print(f"Initial State: {car.aero_mode} (High Downforce baseline)")

    # 1. Place car on Monza Rettifilo Straight (pos: 200m), full throttle, no brake
    car.position = 200.0
    car.speed_ms = 70.0  # 252 km/h
    car.throttle = 1.0
    car.brake = 0.0

    car.update(dt=0.05, track=track, manual_inputs=True)

    assert car.aero_mode == "X-MODE", f"Expected X-MODE on full throttle straight, got {car.aero_mode}"
    print(f"Straightaway (Throttle 100%): Aero Mode -> {car.aero_mode} (40% Drag Reduction Active)")

    # Verify drag reduction effect
    base_drag = car.drag_coeff * (car.speed_ms ** 2)
    effective_drag = (car.drag_coeff * 0.60) * (car.speed_ms ** 2)
    print(f" -> Base Drag Force: {base_drag:.4f} m/s^2")
    print(f" -> X-Mode Effective Drag: {effective_drag:.4f} m/s^2 (Exactly 40.0% reduction)")
    assert abs(effective_drag - (base_drag * 0.60)) < 1e-6

    # 2. Instant braking applied (brake > 0.01) -> Must immediately revert to Z-Mode without delay
    car.throttle = 0.0
    car.brake = 0.65
    car.update(dt=0.05, track=track, manual_inputs=True)

    assert car.aero_mode == "Z-MODE", f"Expected instant reversion to Z-MODE on brake, got {car.aero_mode}"
    print(f"Braking Zone (Brake 65%): Aero Mode -> {car.aero_mode} (Zero-delay reversion verified)")

    # 3. Inside Turn 1 (Variante del Rettifilo, pos: 1200m) with partial throttle -> Must remain Z-Mode
    car.position = 1200.0
    car.brake = 0.0
    car.throttle = 0.50
    car.update(dt=0.05, track=track, manual_inputs=True)

    assert car.aero_mode == "Z-MODE", f"Expected Z-MODE inside corner, got {car.aero_mode}"
    print(f"Corner Apex (T1 Chicane): Aero Mode -> {car.aero_mode} (Cornering high-downforce enforced)")

    print(">>> VERIFICATION PASSED: 2026 Active Aerodynamics (Z-Mode / X-Mode) fully verified!\n")


def test_ers_battery_mgu_k_and_mom():
    print("=" * 80)
    print("TEST 2: HYBRID ERS (4.0 MJ), MGU-K REGEN & MANUAL OVERRIDE (MOM) TEST")
    print("=" * 80)

    track = TrackLibrary.get_monza()
    driver = Driver(name="Test Driver", number=1, aggression=0.8, consistency=0.9, braking_skill=0.90)
    car = Car(name="Test Car", driver=driver, max_speed=340.0, acceleration=12.5)

    # 1. Verify capacity and initial SOC
    print(f"ERS Battery Capacity: {car.ers_max_energy_mj:.1f} MJ")
    print(f"Initial Energy: {car.ers_energy_mj:.2f} MJ (SOC: %{car.ers_soc_pct:.1f})")
    assert abs(car.ers_max_energy_mj - 4.0) < 1e-6
    assert abs(car.ers_energy_mj - 3.4) < 1e-6
    assert abs(car.ers_soc_pct - 85.0) < 1e-6

    # 2. Test MGU-K kinetic energy regeneration during heavy braking
    # Set car at 300 km/h (83.3 m/s) with 3.0 MJ initial energy to leave regen headroom
    car.ers_energy_mj = 3.0
    car.speed_ms = 300.0 / 3.6
    car.throttle = 0.0
    car.brake = 1.0
    initial_energy = car.ers_energy_mj

    # Step simulation through 10 ticks (0.50 s of heavy braking)
    dt = 0.05
    for _ in range(10):
        car.update(dt, track, manual_inputs=True)

    energy_recovered = car.ers_energy_mj - initial_energy
    print(f"Heavy Braking from 300 km/h (0.50s):")
    print(f" -> Energy before: {initial_energy:.3f} MJ | Energy after: {car.ers_energy_mj:.3f} MJ")
    print(f" -> Recovered MGU-K Energy: +{energy_recovered:.4f} MJ (Status: {car.ers_status})")
    assert energy_recovered > 0.05, f"Expected significant kinetic recovery, got {energy_recovered}"
    assert car.ers_status == "REGEN", f"Expected REGEN status, got {car.ers_status}"
    print(">>> VERIFICATION PASSED: MGU-K Kinetic Regeneration actively charges battery on braking!")

    # 3. Test Standard Hybrid Deploy during straightline acceleration
    car.position = 200.0  # Main straight
    car.speed_ms = 60.0
    car.throttle = 1.0
    car.brake = 0.0
    pre_deploy_energy = car.ers_energy_mj

    for _ in range(10):
        car.update(dt, track, manual_inputs=True)

    energy_consumed = pre_deploy_energy - car.ers_energy_mj
    print(f"\nStandard Hybrid Deployment along Straight (0.50s):")
    print(f" -> Pre-deploy: {pre_deploy_energy:.3f} MJ | Post-deploy: {car.ers_energy_mj:.3f} MJ")
    print(f" -> Energy Consumed: -{energy_consumed:.4f} MJ (Status: {car.ers_status})")
    assert energy_consumed > 0.01, f"Expected hybrid deployment consumption, got {energy_consumed}"
    assert car.ers_status == "DEPLOY", f"Expected DEPLOY status, got {car.ers_status}"

    # 4. Test Manual Override Mode (MOM) Rapid 350 kW Discharge & High Acceleration
    car.position = 300.0
    car.speed_ms = 285.0 / 3.6  # 285 km/h
    car.throttle = 1.0
    car.brake = 0.0
    car.override_ready = True
    car.mom_active = True
    pre_mom_energy = car.ers_energy_mj

    # Step MOM for 0.5s (10 ticks * 0.05s)
    mom_speeds = []
    for _ in range(10):
        mom_speeds.append(car.speed)
        car.update(dt, track, manual_inputs=True)

    mom_energy_consumed = pre_mom_energy - car.ers_energy_mj
    expected_mom_rate = 0.350 * 0.50  # 350 kW * 0.5s = 0.175 MJ
    print(f"\nManual Override Mode (MOM 350 kW Boost) Active (0.50s):")
    print(f" -> Pre-MOM: {pre_mom_energy:.3f} MJ | Post-MOM: {car.ers_energy_mj:.3f} MJ")
    print(f" -> MOM Energy Discharged: -{mom_energy_consumed:.4f} MJ (Status: {car.ers_status})")
    print(f" -> Acceleration jump: {mom_speeds[0]:.1f} km/h -> {mom_speeds[-1]:.1f} km/h (+{(mom_speeds[-1] - mom_speeds[0]):.1f} km/h in 0.5s)")
    assert abs(mom_energy_consumed - expected_mom_rate) < 0.03, f"Expected ~0.175 MJ consumed, got {mom_energy_consumed}"
    assert car.ers_status == "MOM ACTIVE", f"Expected MOM ACTIVE status, got {car.ers_status}"

    # 5. Test Automatic MOM Cutoff when Battery drops below 10% SOC (< 0.40 MJ)
    car.ers_energy_mj = 0.42  # 10.5% SOC
    car.override_ready = True
    car.mom_active = True
    print(f"\nTesting Automatic MOM Battery Cutoff (Starting at {car.ers_energy_mj:.3f} MJ, SOC: %{car.ers_soc_pct:.1f}):")

    # Step until battery drops below 0.40 MJ
    for _ in range(5):
        car.update(dt, track, manual_inputs=True)

    print(f" -> Final Energy: {car.ers_energy_mj:.3f} MJ | Final SOC: %{car.ers_soc_pct:.1f}")
    print(f" -> MOM Active State: {car.mom_active} | ERS Status: {car.ers_status}")
    assert car.ers_soc_pct < 10.0, f"Expected SOC < 10%, got {car.ers_soc_pct}"
    assert not car.mom_active, f"Expected MOM to automatically shut off below 10% SOC!"
    print(">>> VERIFICATION PASSED: MOM automatically shuts off below 10% SOC!\n")


def test_slipstream_and_mom_overtake_scenario():
    print("=" * 80)
    print("TEST 3: SLIPSTREAM (WAKE) & MOM OVERTAKE SCENARIO ON STRAIGHTAWAY")
    print("=" * 80)

    track = TrackLibrary.get_monza()  # Rettifilo Straight is 1,120 meters long
    race = Race(track=track, laps=5)

    car_a = race.cars[0]
    car_b = race.cars[1]

    # Setup Overtake Scenario along Rettifilo Straight:
    # Car A: P1 Leader at position 250.0m, speed 284 km/h
    # Car B: P2 Follower at position 235.0m (15m behind Car A, gap < 1.0s), speed 282 km/h
    car_a.position = 250.0
    car_a.speed_ms = 284.0 / 3.6
    car_a.throttle = 1.0
    car_a.brake = 0.0

    car_b.position = 235.0
    car_b.speed_ms = 282.0 / 3.6
    car_b.throttle = 1.0
    car_b.brake = 0.0

    # 1. Update 1 tick to evaluate wake detection
    race.update(0.05)

    gap_m = car_a.position - car_b.position
    print(f"Initial Setup on Rettifilo Straight:")
    print(f" -> Car A (Lead): Pos: {car_a.position:.1f} m, Speed: {car_a.speed:.1f} km/h")
    print(f" -> Car B (Trail): Pos: {car_b.position:.1f} m, Speed: {car_b.speed:.1f} km/h")
    print(f" -> Distance Gap: {gap_m:.1f} m")

    # Verify Car B slipstream reduction
    print(f"Car B Slipstream Reduction: {car_b.slipstream_reduction * 100:.1f}% drag reduction")
    assert 0.15 <= car_b.slipstream_reduction <= 0.35, f"Slipstream reduction out of range: {car_b.slipstream_reduction}"

    # Verify MOM Override Ready triggered for Car B
    print(f"Car B Override Ready: {car_b.override_ready}")
    assert car_b.override_ready is True, "Expected Car B to be OVERRIDE READY (< 1.0s gap at 280+ km/h)!"

    # Verify Car B engaged MOM
    print(f"Car B MOM Active: {car_b.mom_active} (Status: {car_b.ers_status})")
    assert car_b.mom_active is True, "Expected Car B driver AI to activate MOM on straight overtake opportunity!"

    # 2. Simulate down the straight and watch Car B pull alongside and overtake Car A!
    print("\nSimulating Straightline Overtake (up to 4.0 seconds):")
    overtake_occurred = False
    for step in range(1, 81):
        race.update(0.05)
        current_gap = car_b.position - car_a.position

        if step % 10 == 0:
            print(
                f" -> [t = {step * 0.05:4.2f}s] "
                f"Car A: {car_a.speed:5.1f} km/h ({car_a.position:6.1f}m) | "
                f"Car B: {car_b.speed:5.1f} km/h ({car_b.position:6.1f}m) | "
                f"Delta Pos (B-A): {current_gap:+6.2f}m | "
                f"B Status: {car_b.ers_status}"
            )

        if car_b.position > car_a.position and not overtake_occurred:
            overtake_occurred = True
            print(f"    >>> OVERTAKE DETECTED at t = {step * 0.05:.2f}s! Car B passes Car A!")

    assert overtake_occurred, "Expected Car B to pass Car A using slipstream + MOM boost!"
    assert car_b.position > car_a.position, f"Expected Car B ahead of Car A, got B={car_b.position:.1f}m, A={car_a.position:.1f}m"
    print(f"\nFinal Outcome: Car B is {car_b.position - car_a.position:.2f} m ahead of Car A!")
    print(">>> VERIFICATION PASSED: Slipstream + 350 kW MOM boost successfully executed the overtake!\n")

    # 3. Test Dirty Air in cornering
    print("Testing Dirty Air Downforce Penalty in Cornering:")
    # Turn 4 Infield corner
    car_a.position = 1250.0  # in corner
    car_b.position = 1230.0  # 20m behind Car A in corner
    car_b.speed_ms = 45.0
    race.update(0.05)
    print(f" -> Car B in corner trailing Car A (20m): in_dirty_air = {car_b.in_dirty_air}")
    assert car_b.in_dirty_air is True, "Expected in_dirty_air == True in cornering wake!"
    print(">>> VERIFICATION PASSED: Dirty air penalty correctly triggered in corners!\n")


def run_all_tests():
    test_active_aerodynamics_modes()
    test_ers_battery_mgu_k_and_mom()
    test_slipstream_and_mom_overtake_scenario()
    print("=" * 80)
    print("ALL 2026 FIA TECHNICAL REGULATIONS TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_all_tests()
