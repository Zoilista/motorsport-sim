# 🏎️ Motorsport Simulation — Pit-Wall Telemetry & Race Control

> *A deterministic, segment-based motorsport engineering simulation and 2026 technical regulations telemetry testbed.*

A high-fidelity Formula 1 telemetry, race strategy, and vehicle dynamics simulation built in **Python 3.11+** and **PySide6 (Qt for Python)**. Designed to mirror professional motorsport data-engineering workbenches with SI-unit kinematics, 2026 technical regulations, 4-wheel tyre thermodynamics, dynamic fuel mass scaling, and pit strategy.

---

## ⚡ Key Highlights & Architecture

- **Deterministic Kinematic Core (`simulation/`):** Segment-based circuit geometry with quadratic aerodynamic drag, dynamic fuel mass scaling ($\approx 0.35\text{ s} / 10\text{ kg}$ lap time penalty), driver braking AI ($a \approx 4.3\text{G}$ decelerations), and continuous 20 Hz numerical integration.
- **2026 FIA Technical Regulations:**
  - **Active Aerodynamics:** Automated dual-state wing actuation (**Z-Mode** for high downforce in braking/corners, **X-Mode** with 40% drag reduction on straights yielding $+16\text{ km/h}$ top speed).
  - **Aerodynamic Wake:** Distance-based slipstream on straights (up to 35% drag drop) and dirty-air cornering downforce penalties.
  - **Hybrid ERS & Manual Override Mode (MOM):** 4.0 MJ battery storage, MGU-K kinetic braking regeneration (up to 350 kW), and automated MOM overtakes under $\Delta t \le 1.0\text{ s}$ detection gap.
- **4-Wheel Thermodynamic & Wear Kinetics (`simulation/tyre.py`):**
  - Independent cornering, braking, and traction heat fluxes across **FL, FR, RL, and RR**.
  - Dynamic lateral load transfer (e.g., severe thermal build-up on outside right tyres in anti-clockwise layouts like Istanbul Park Turn 8).
  - Authentic compound specifications: **Soft (C3)**, **Medium (C2)**, and **Hard (C1)** with realistic degradation crossovers.
- **Dynamic Race Strategy & Pit Lane Loop:**
  - 80 km/h pit speed limiter enforcement.
  - 2.4-second stationary pit box tyre changes and autonomous AI pit calls (`BOX THIS LAP`) based on tyre wear thresholds.
- **High-Frequency Telemetry Logging (`simulation/telemetry_recorder.py`):**
  - Continuous 20 Hz CSV telemetry export (`telemetry_exports/race_telemetry.csv`) ready for offline engineering analytics, Pandas, Matplotlib, and FastF1 integration.
- **Layout Scuderia (Apple-Clean UI in PySide6):**
  - Real-world 2D circuit GPS/spline geometries with aspect-ratio-preserved scaling (`fitInView`).
  - Edge-to-edge live speed telemetry waveform (0–350 km/h calibrated grid).
  - Real-time Leaderboard with compound pills (`[S]`, `[M]`, `[H]`), tyre age, and pit status.
  - Compact 6-metric bottom telemetry deck (`SPEED`, `GEAR`, `RPM`, `THROTTLE`, `BRAKE`, `AERO MODE`).
  - Interactive **Setup Workbench Modal** (press `Space` to tune kinematics and trigger manual `BOX BOX` calls).

---

## 🔬 Engineering Rigor & Model Validation

For a comprehensive mathematical breakdown of kinematic equations, aerodynamic assumptions, 4-wheel thermodynamic flux, and deliberate simplifications versus 6-DOF multi-body vehicle simulators, see **[MODEL_ASSUMPTIONS.md](MODEL_ASSUMPTIONS.md)**.

### Parametric Sensitivity Benchmarks (`scratch/run_sensitivity_study.py`)

The simulation contains an automated parametric sensitivity suite that systematically audits physical models against empirical Formula 1 engineering telemetry:

```bash
python scratch/run_sensitivity_study.py
```

| Benchmark Parameter | Simulation Result | Empirical F1 Benchmark | Status |
| :--- | :---: | :---: | :---: |
| **Fuel Mass Penalty (Monza)** | **$0.360\text{ s} / 10\text{ kg}$** | $0.30 - 0.40\text{ s} / 10\text{ kg}$ | **PASS** |
| **Active Aero X-Mode vs Z-Mode $\Delta v_{\max}$** | **$+16.0\text{ km/h}$** ($336.0$ vs $320.0$) | $+15 - 25\text{ km/h}$ | **PASS** |
| **Active Aero X-Mode Lap Delta** | **$-1.300\text{ s}$** on Monza | $-1.0 - 2.0\text{ s}$ | **PASS** |
| **Tyre Wear Ratio (Soft vs Medium)** | **$1.92\times$** ($16.9\%$ vs $8.8\%$) | Nominal $1.75\times$ | **PASS** |
| **20 Hz CSV Telemetry Export** | **$2,165\text{ frames}$** ($157\text{ KB}$) | Continuous 20 Hz sync | **PASS** |

Structured benchmark outputs are serialized to `scratch/sensitivity_results.json` after every run.

---

## 🏁 Supported Circuit Library

| Circuit | Length | Direction | Key Architectural Characteristic |
| :--- | :---: | :---: | :--- |
| **Autodromo Nazionale Monza** | 5,793 m | Clockwise | Temple of Speed: Low drag, heavy braking into Variante del Rettifilo. |
| **Intercity Istanbul Park** | 5,338 m | Anti-Clockwise | Quad-apex Turn 8: Extreme lateral G and asymmetric right tyre wear. |
| **Silverstone Circuit** | 5,891 m | Clockwise | Modern Arena layout: Flowing Maggotts-Becketts-Chapel high-speed complex. |
| **Prototype GP Circuit** | 5,200 m | Clockwise | Balanced development test bench. |

---

## 🛠️ Project Structure

```text
motorsport-sim/
├── main.py                         # Application entry point & Qt event loop
├── MODEL_ASSUMPTIONS.md            # Peer-reviewed engineering report & physics assumptions
├── simulation/                     # Headless deterministic simulation core
│   ├── car.py                      # Longitudinal dynamics, fuel mass scaling & aero
│   ├── driver.py                   # AI aggression, consistency & tyre management
│   ├── race.py                     # Multi-car coordinator, gaps, AI strategy
│   ├── telemetry.py                # Telemetry snapshot dataclasses
│   ├── telemetry_recorder.py       # High-frequency 20 Hz CSV telemetry logger
│   ├── track.py                    # Segment-based geometry & arc lengths
│   ├── track_library.py            # Real-world circuit GPS spline waypoints
│   └── tyre.py                     # 4-wheel thermal flux & compound kinetics
├── telemetry_exports/              # Exported CSV telemetry logs
│   └── race_telemetry.csv          # 20 Hz engineering telemetry dataset
├── ui/                             # Modern PySide6 telemetry interface
│   ├── theme.py                    # Dark carbon tokens & typography
│   ├── main_window.py              # 3-column Layout Scuderia master shell
│   ├── view_models/                # MVVM abstraction layer
│   └── widgets/                    # Modular telemetry cards, canvas & dialogs
└── scratch/                        # Automated regression & QA stress suites
    ├── full_system_test.py         # 20 Hz multi-lap end-to-end audit
    ├── qa_stress_test.py           # GUI stress & mathematical limit audit
    ├── run_sensitivity_study.py    # Automated parametric sensitivity benchmarks
    ├── sensitivity_results.json    # Machine-readable benchmark outputs
    └── test_strategy_pitstops.py   # Tyre crossover & pit limiter verification
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- Virtual environment (`venv`)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Zoilista/motorsport-sim.git
   cd motorsport-sim
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install PySide6 numpy
   ```

---

## 🎮 Running the Simulation

Run the pit-wall desktop client:
```bash
python main.py
```

### Keyboard & UI Controls

- **Spacebar**: Toggle pause / open the **Setup Workbench & Diagnostics Dialog**.
- **Top Bar Circuit Dropdown**: Switch circuits dynamically mid-session.
- **Leaderboard Click**: Select and focus telemetry view on **Driver A (#07)** or **Driver B (#22)**.
- **Workbench Controls**: Live-tune downforce, mechanical grip, acceleration, and trigger manual **`CALL BOX BOX`** pit stops.

---

## 🧪 Automated Testing & Diagnostics

```bash
# Run Flagship Parametric Sensitivity & Model Validation Study
python scratch/run_sensitivity_study.py

# Run Senior QA Edge-Case & Stress Audit
python scratch/qa_stress_test.py

# Run Full-Stack 20 Hz End-to-End Multi-Lap Regression
python scratch/full_system_test.py

# Run Tyre Compound Crossover & Pit Lane Test
python scratch/test_strategy_pitstops.py
```

---

## ⚖️ Quality Assurance & Code Standards

- **Pyright / Mypy**: 0 Errors, 0 Warnings (Strict type safety)
- **Flake8 / Ruff**: 100% Clean (PEP 8 compliant)
- **Architecture**: Decoupled Model-View-ViewModel (MVVM)
- **Mathematical Rigor**: SI units throughout ($m$, $m/s$, $m/s^2$, $kg$, $kW$, $MJ$, $^\circ C$)