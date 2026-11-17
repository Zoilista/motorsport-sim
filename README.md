# Motorsport Simulation
### A Deterministic Vehicle Simulation & Real-Time Telemetry Platform

A Python-based motorsport engineering project combining **mathematical modeling, vehicle dynamics, race strategy, telemetry processing, and desktop visualization**.

The project provides a deterministic, segment-based vehicle simulation engine and a PySide6 race-control dashboard. It explores simplified motorsport engineering models inspired by modern Formula racing systems, including active aerodynamics, hybrid energy recovery, tyre degradation, and pit strategy.

> **Engineering Scope**
>
> This is an independent simulation and engineering workbench, not a professional-grade vehicle dynamics simulator or an FIA-certified implementation. Its models use deliberate simplifications to make vehicle behavior, energy systems, tyre dynamics, and race strategy computationally accessible. Model assumptions and limitations are documented in [`MODEL_ASSUMPTIONS.md`](MODEL_ASSUMPTIONS.md).

---

## Key Features

### 1. Vehicle Dynamics & Simulation Engine

The simulation core uses a deterministic, segment-based approach to model vehicle behavior.

- Longitudinal vehicle dynamics using SI units.
- Quadratic aerodynamic drag and rolling resistance.
- Fuel-mass-dependent performance scaling.
- Acceleration, braking, and speed management.
- Cornering target speeds based on track geometry and tyre grip.
- Driver behavior parameters for aggression, consistency, braking skill, and tyre management.
- Fixed-step numerical integration with a nominal timestep of `0.05 seconds`.

### 2. Tyre Thermal & Degradation Model

A four-wheel tyre model tracks each tyre independently:

- Front-left, front-right, rear-left, and rear-right states.
- Soft, Medium, and Hard compound configurations.
- Temperature-dependent grip behavior.
- Wear-dependent grip reduction.
- Heat generation from braking, cornering, traction, and rolling resistance.
- Temperature-dependent cooling.
- Driver tyre-management parameters influencing degradation.

The model separates thermal grip effects, wear effects, and compound characteristics.

### 3. Aerodynamics & Hybrid Energy Systems

The simulation includes simplified systems inspired by modern Formula racing technology.

**Active Aerodynamics**
- Z-MODE and X-MODE operating states.
- Mode-dependent aerodynamic drag.
- Automated mode transitions based on driving conditions.
- Cornering and straight-line behavior.

**Aerodynamic Wake**
- Distance-dependent slipstream effect.
- Reduced drag while following another car.
- Dirty-air downforce penalty during cornering.

**Energy Recovery & Deployment**
- 4.0 MJ battery capacity.
- MGU-K power and regenerative braking model with a 350 kW limit.
- State-of-charge tracking.
- Energy deployment and recovery.
- MOM (Manual Override Mode) simulation for qualifying-style or overtake scenarios.

These are configurable model parameters and simplified behaviors, not claims of exact real-world regulatory implementation.

### 4. Race Strategy & Pit Stop System

- Two-driver race simulation.
- Dynamic race standings based on completed distance.
- Tyre wear-based automatic pit requests.
- Manual pit stop commands through the dashboard.
- Next-compound selection.
- Pit lane speed limiter.
- Pit lane, pit box, and race-state tracking.

### 5. Telemetry & Data Export

The telemetry system exposes vehicle and race information for visualization and offline analysis.

Available telemetry includes:

- Speed, throttle, and brake input.
- Gear and engine RPM.
- Tyre temperatures and wear.
- Fuel level and fuel flow.
- ERS energy and state of charge.
- Aerodynamic mode.
- Tyre compound and stint information.
- Pit stop and race state.

Telemetry can be exported to CSV for further analysis using tools such as Python, Pandas, or Matplotlib.

The included recorder writes selected telemetry fields; its sampling frequency depends on how frequently it is called by the application.

### 6. PySide6 Race-Control Dashboard

The desktop interface is designed around a motorsport pit-wall workflow.

- Three-column race-control dashboard.
- Interactive driver leaderboard.
- Custom 2D circuit visualization.
- Live speed telemetry graph with a rolling history window.
- Individual four-wheel tyre temperature and wear displays.
- Fuel and ERS monitoring.
- Lap and sector timing panels.
- Circuit selection.
- Interactive vehicle setup workbench.
- Manual pit stop controls.
- Pause, resume, and session-finished states.

The dashboard uses a nominal 50 ms update interval, corresponding to a target update rate of 20 Hz.

---

## Software Architecture

The project separates simulation logic, presentation data, and graphical interface responsibilities.

```text
                 ┌──────────────────────────┐
                 │       main.py            │
                 │   Application Entry     │
                 └────────────┬─────────────┘
                              │
                 ┌────────────▼─────────────┐
                 │       PySide6 UI         │
                 │  Dashboard & Widgets     │
                 └────────────┬─────────────┘
                              │
                 ┌────────────▼─────────────┐
                 │       ViewModel           │
                 │ Snapshots, Timing, Data  │
                 └────────────┬─────────────┘
                              │
                 ┌────────────▼─────────────┐
                 │     Simulation Core       │
                 │ Race, Car, Track, Tyres  │
                 └──────────────────────────┘
```

### Architectural Responsibilities

| Layer | Responsibility |
|---|---|
| `simulation/` | Vehicle dynamics, race progression, tyres, tracks, and telemetry |
| `ui/view_models/` | Converts simulation state into UI-ready snapshots and standings |
| `ui/widgets/` | Reusable dashboard components and visualizations |
| `ui/main_window.py` | Main application orchestration |
| `ui/theme.py` | Centralized colors, typography, and QSS styling |
| `telemetry_exports/` | Exported telemetry datasets |
| `MODEL_ASSUMPTIONS.md` | Mathematical assumptions and model limitations |

The interface follows an **MVVM-inspired separation of concerns**, with a ViewModel adapter between the simulation engine and UI widgets.

---

## Supported Circuits

The dashboard provides a circuit selection interface for the following layouts:

| Circuit | Configured Length |
|---|---:|
| Autodromo Nazionale Monza | 5,793 m |
| Intercity Istanbul Park | 5,338 m |
| Silverstone Circuit | 5,891 m |
| Prototype GP Circuit | 5,200 m |

Circuit geometry and segment data are simplified for simulation purposes. The 2D dashboard visualization is a spline-based representation, not a precision GPS or CAD model.

---

## Technology Stack

| Technology | Application |
|---|---|
| Python 3.11+ | Core application and simulation logic |
| PySide6 / Qt | Desktop GUI and event-driven interface |
| NumPy | Numerical computing |
| Object-Oriented Programming | Vehicle, race, track, and tyre models |
| Dataclasses | Structured simulation and telemetry data |
| CSV | Telemetry export |
| QPainter | Custom 2D visualization |
| QSS | Centralized Qt interface styling |

---

## Project Structure

```text
motorsport-sim/
│
├── main.py
│
├── simulation/
│   ├── car.py
│   ├── driver.py
│   ├── race.py
│   ├── track.py
│   ├── track_library.py
│   ├── tyre.py
│   ├── telemetry.py
│   └── telemetry_recorder.py
│
├── ui/
│   ├── main_window.py
│   ├── theme.py
│   ├── track_view.py
│   │
│   ├── view_models/
│   │   └── race_view_model.py
│   │
│   └── widgets/
│       ├── leaderboard.py
│       ├── telemetry_panel.py
│       ├── telemetry_card.py
│       ├── telemetry_graph.py
│       ├── track_view.py
│       ├── race_status_panel.py
│       ├── tyre_card.py
│       ├── energy_card.py
│       ├── setup_workbench.py
│       └── car_setup_view.py
│
├── telemetry_exports/
│   └── race_telemetry.csv
│
└── MODEL_ASSUMPTIONS.md
```

---

## Getting Started

### Prerequisites

- Python 3.11 or newer
- pip
- A desktop environment supported by PySide6

### Installation

Clone the repository:

```bash
git clone https://github.com/Zoilista/motorsport-sim.git
cd motorsport-sim
```

Create a virtual environment:

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install PySide6 numpy
```

### Run

```bash
python main.py
```

---

## Dashboard Controls

| Control | Action |
|---|---|
| Space | Open or toggle the setup workbench / pause workflow |
| Circuit selector | Change the active circuit |
| Leaderboard row | Select a driver |
| Setup workbench | Adjust vehicle parameters |
| Pit controls | Request a pit stop and select the next tyre compound |
| Resume | Continue the simulation |

---

## Model Assumptions & Limitations

The simulation intentionally prioritizes an understandable, modular engineering model over high-fidelity vehicle dynamics.

Current limitations include:

- Segment-based longitudinal vehicle dynamics rather than a complete 6-DOF vehicle model.
- Simplified aerodynamic drag and downforce relationships.
- Simplified tyre thermal and wear behavior rather than a transient Pacejka tyre model.
- No CFD or wind-tunnel validation.
- Simplified circuit geometry and corner representation.
- Approximate time-gap calculations based on distance and current speed.
- Fixed-step numerical integration, which limits timing resolution.
- Model parameters are not calibrated against a complete external real-world telemetry dataset.

For the mathematical details, equations, parameter values, and implementation assumptions, see [`MODEL_ASSUMPTIONS.md`](MODEL_ASSUMPTIONS.md).

---

## Project Direction

The project is an ongoing exploration of the intersection between:

- Mathematical modeling
- Numerical simulation
- Vehicle dynamics
- Data processing and telemetry
- Software architecture
- Engineering visualization

Future development can focus on improving model validation, automated testing, telemetry analysis, simulation accuracy, and extensibility.

---

**Built as an independent engineering and software development project.**
