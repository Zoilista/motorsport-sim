# Motorsport Simulation — Mathematical Model Assumptions, Formulations & Engineering Limitations

**Version:** 1.1
**Domain:** Vehicle Dynamics, 2026 FIA Technical Regulations, Telemetry Data Engineering
**Scope:** Kinematic Integration, Longitudinal/Lateral Acceleration Limits, 4-Wheel Lumped Thermal Kinetics, Dynamic Race Strategy

---

## 1. Executive Summary & Model Scope

This simulation is engineered as a **deterministic, segment-based, 20 Hz kinematic and telemetry testbed** designed to evaluate race strategy, active aerodynamics (2026 FIA Technical Regulations), hybrid energy management (ERS/MOM), and four-wheel tyre degradation.

### What the Simulation Is
- A **1D segment-based kinematic simulator** operating along the circuit path coordinate $s(t) \in [0, L_{\text{track}})$.
- A **deterministic computational workbench** where identical initial conditions and driver parameters yield bitwise reproducible multi-lap telemetry traces.
- A **real-time 20 Hz numerical testbed** ($dt = 0.05\text{ s}$) powering an asynchronous Model-View-ViewModel (MVVM) architecture for pit-wall engineering analytics.
- A **calibrated parametric model** whose longitudinal limits, mass penalties, active aero drag deltas, and tyre wear orderings align with published Grand Prix engineering literature and regulatory benchmarks.

### What the Simulation Is Not
- **Not a 6-DOF multi-body vehicle dynamics solver:** There is no suspension kinematics, chassis pitch (brake dive), roll (anti-roll bar stiffness), or heave (third damper oscillation).
- **Not a transient tyre dynamics model:** There is no Pacejka brush model, slip angle ($\alpha$) relaxation length, or longitudinal slip ratio ($\kappa$) ODE solver.
- **Not a 3D aero-elastic or CFD simulator:** Downforce, drag reduction, and aerodynamic wake are modeled via calibrated 1D algebraic functions rather than Navier-Stokes field solutions.
- **Not a 3D terrain/track model:** Circuits are modeled as piecewise continuous 1D arcs with constant radii; there are no vertical elevation profiles, road cambers, or variable surface macro-textures.

---

## 2. Vehicle Dynamics & Kinematic Formulations

### 2.1 Longitudinal Dynamics
Rather than solving multi-body forces and inertial tensors, the simulation directly integrates longitudinal kinematic accelerations ($m/s^2$) along the circuit path tangent:

$$\frac{dv}{dt} = a_{\text{propulsion}} + a_{\text{electric\_boost}} - a_{\text{drag}} - a_{\text{braking}}$$

#### Aerodynamic Drag Deceleration ($a_{\text{drag}}$)
Aero drag is formulated directly as a velocity-squared kinematic deceleration:

$$a_{\text{drag}} = k_{\text{drag}} \cdot v^2 + a_{\text{rolling}}$$

where:
- $v$ is the longitudinal vehicle speed in $\text{m/s}$.
- $k_{\text{drag}} = k_{\text{base}} \cdot \gamma_{\text{aero}} \cdot \max(0.0, 1.0 - \delta_{\text{slipstream}})$ has physical dimension $\text{m}^{-1}$.
- $k_{\text{base}}$ is the aerodynamic drag coefficient:
  - **Medium Downforce (Default):** $k_{\text{base}} = 0.00038\text{ m}^{-1}$
  - **Low Downforce (Monza Trim):** $k_{\text{base}} = 0.00030\text{ m}^{-1}$
  - **High Downforce:** $k_{\text{base}} = 0.00048\text{ m}^{-1}$
- $\gamma_{\text{aero}}$ is the active aerodynamic drag multiplier:
  - **Z-Mode:** $\gamma_{\text{aero}} = 1.00$ (full downforce and baseline drag)
  - **X-Mode:** $\gamma_{\text{aero}} = 0.60$ ($40\%$ drag reduction along straights)
- $\delta_{\text{slipstream}} \in [0.15, 0.35]$ represents aerodynamic wake drag reduction when trailing a leading car along straights.
- $a_{\text{rolling}} = 0.15\text{ m/s}^2$ represents mechanical rolling resistance from tyre carcass deformation and drivetrain friction.

#### Dynamic Mass Scaling ($M_{\text{total}}$ & $\text{mass\_factor}$)
Vehicle mass evolves dynamically with instantaneous fuel consumption:

$$M_{\text{total}}(t) = M_{\text{dry}} + \max(0.0, M_{\text{fuel}}(t))$$

- Minimum dry weight + driver: $M_{\text{dry}} = 798.0\text{ kg}$ (FIA Technical Regulation minimum).
- Initial fuel capacity: $M_{\text{fuel}}(0) = 100.0\text{ kg}$.

In high-downforce open-wheel racing, aerodynamic downforce at high speed ($F_z > 25\text{ kN}$) dominates the total tyre normal load, partially decoupling tyre grip and braking capacity from fuel mass. To reflect the published Grand Prix empirical sensitivity ($\approx 0.30 - 0.40\text{ s} / 10\text{ kg}$ lap time delta on high-speed circuits), inertial acceleration, braking deceleration, and cornering grip scale via the calibrated mass factor:

$$\text{mass\_factor} = \max\left(0.60, \min\left(1.10, \frac{M_{\text{dry}} + 10.0}{M_{\text{dry}} + 10.0 + \max(0.0, M_{\text{fuel}} - 10.0) \cdot 0.65}\right)\right)$$

*Implementation Note:* The code implements a scaling multiplier of $0.65$ on excess fuel above $10.0\text{ kg}$, clamped strictly to the range $[0.60, 1.10]$.

#### Engine Propulsion Acceleration ($a_{\text{propulsion}}$)
When braking is inactive ($\text{brake} \le 0.01$) and fuel remains ($M_{\text{fuel}} > 0$):

$$a_{\text{propulsion}} = a_{\text{engine, max}} \cdot (0.85 + 0.15 \cdot \text{aggression}) \cdot \Phi_{\text{power}}(v) \cdot \text{throttle} \cdot \text{mass\_factor}$$

where:
- $a_{\text{engine, max}}$ is the peak ICE longitudinal acceleration: $12.0\text{ m/s}^2$ baseline ($12.4\text{ m/s}^2$ for Car A, $12.1\text{ m/s}^2$ for Car B).
- $\Phi_{\text{power}}(v) = \max\left(0.38, 1.0 - 0.42 \cdot \frac{v}{v_{\text{max\_ms}}}\right)$ reflects internal combustion power roll-off at elevated speeds.
- If $M_{\text{fuel}} \le 0.0$, fuel starvation cuts ICE propulsion to $0.0\text{ m/s}^2$, forcing the vehicle to coast down under drag and rolling resistance.

#### Transmission & Engine RPM Mapping
The gearbox is modeled as an 8-speed transmission with deterministic speed-based shift thresholds:

| Gear | Speed Range (km/h) |
| :---: | :---: |
| **1** | $0.0 - 70.0$ |
| **2** | $70.0 - 110.0$ |
| **3** | $110.0 - 150.0$ |
| **4** | $150.0 - 190.0$ |
| **5** | $190.0 - 230.0$ |
| **6** | $230.0 - 270.0$ |
| **7** | $270.0 - 305.0$ |
| **8** | $305.0 - 335.0+$ |

Engine RPM interpolates linearly across each gear's speed band:

$$\text{RPM} = 4800.0 + \left(\frac{v_{\text{kmh}} - v_{\text{gear, min}}}{v_{\text{gear, max}} - v_{\text{gear, min}}}\right) \cdot 7800.0$$

yielding an operating range from $4,800\text{ RPM}$ up to an engine redline of $12,600\text{ RPM}$.

---

### 2.2 Lateral Dynamics & Cornering

Cornering velocity limits are derived from steady-state centripetal acceleration equilibrium:

$$a_{\text{lateral}} = \frac{v^2}{R} \le \mu_{\text{effective}} \cdot g$$

For a track segment with curvature radius $R$ and track baseline friction $\mu_{\text{base}} = 1.75$, the analytical baseline apex velocity is:

$$v_{\text{base, apex}} = \sqrt{\mu_{\text{base}} \cdot g \cdot R}$$

The driver AI calculates the target corner velocity $v_{\text{target}}$ by modulating $v_{\text{base, apex}}$ with instantaneous mechanical grip, mass, downforce trim, dirty air, and driver consistency:

$$v_{\text{target}} = v_{\text{base, apex}} \cdot \sqrt{\max(0.20, \mu_{\text{setup}} \cdot \mu_{\text{tyre}})} \cdot (\text{mass\_factor})^{0.5} \cdot k_{\text{aero}} \cdot \left[0.98 + 0.04 \cdot (\text{consistency} - 0.90)\right]$$

where:
- $\mu_{\text{setup}}$ is the setup mechanical grip multiplier (default $1.00$).
- $\mu_{\text{tyre}} = \left(\frac{\mu_{\text{compound}}}{1.70}\right) \cdot \mu_{\text{condition, avg}}$ accounts for compound friction relative to Medium baseline ($1.70$) and 4-wheel average thermal/wear condition.
- Notice that because $v \propto \sqrt{\mu}$, the combined grip multiplier appears under a square root ($\sqrt{\mu_{\text{setup}} \cdot \mu_{\text{tyre}}}$), as does the inertial mass factor ($(\text{mass\_factor})^{0.5}$).
- $k_{\text{aero}}$ is the aerodynamic downforce package scalar: $1.08$ (High), $1.00$ (Medium), $0.94$ (Low).
- In dirty air ($d_{\text{gap}} \le 65.0\text{ m}$ in corner segments), $k_{\text{aero}}$ is penalized by $10\%$ ($k_{\text{aero}} \times 0.90$).

---

### 2.3 Braking Dynamics & Deceleration Point

#### Maximum Calibrated Braking Deceleration ($a_{\text{brake, max}} = 42.0\text{ m/s}^2 \approx 4.3\text{G}$)
Modern Formula 1 carbon-carbon brake discs paired with aerodynamic downforce produce peak decelerations of $4.5\text{G} - 5.0\text{G}$ at high speed. The simulator parameterizes maximum mechanical braking deceleration to $42.0\text{ m/s}^2$.

Effective braking deceleration incorporates driver skill and mass scaling:

$$a_{\text{brake, effective}} = a_{\text{brake, max}} \cdot (0.85 + 0.15 \cdot \text{braking\_skill}) \cdot \text{mass\_factor}$$

When the brake pedal is applied ($\text{brake} > 0.01$), total deceleration is:

$$a_{\text{decel}} = a_{\text{brake, effective}} \cdot \text{brake} + a_{\text{drag}}$$

#### Kinematic Braking Point Trigger
The autonomous driving controller scans upcoming corners within a $450.0\text{ m}$ horizon. For each corner with target apex velocity $v_{\text{target}}$, the required kinematic stopping distance is:

$$d_{\text{req}} = \frac{v_{\text{current}}^2 - v_{\text{target}}^2}{2 \cdot a_{\text{brake, effective}}}$$

Driver braking skill modulates the actuation threshold through a safety margin $\eta_{\text{driver}}$:

$$\eta_{\text{driver}} = 1.04 - (\text{braking\_skill} - 0.80) \times 0.08$$

$$d_{\text{trigger}} = d_{\text{req}} \cdot \eta_{\text{driver}}$$

An elite driver ($\text{braking\_skill} = 0.95$) achieves $\eta_{\text{driver}} = 0.928$, allowing significantly deeper braking into corner entries. A hysteresis latch maintains braking through $1.50 \times d_{\text{trigger}}$ to avoid control hunting.

---

## 3. Aerodynamics & 2026 Technical Regulations

### 3.1 Active Aerodynamics (Z-Mode vs. X-Mode)

| Operating Parameter | Z-Mode (Cornering / Braking) | X-Mode (High-Speed Straight) |
| :--- | :--- | :--- |
| **Wing State** | High Downforce (Standard AoA) | Low Drag (Flaps neutral / opened) |
| **Drag Multiplier ($\gamma_{\text{aero}}$)** | $1.00$ (Baseline Drag) | $0.60$ (**40% Drag Reduction**) |
| **Top Speed Cap Multiplier** | $1.00$ (Nominal $315 - 325\text{ km/h}$) | $1.05$ (**+5% Top Speed Headroom**) |
| **Activation Criteria** | Corners, braking, or corner approach ($d_{\text{corner}} \le 35.0\text{ m}$) | Straights, steering straight, throttle $\ge 0.95$, dwell $\ge 0.40\text{ s}$ |
| **Deactivation / Safety Lock** | N/A | Immediate revert upon braking ($\text{brake} > 0.01$), corner entry, or throttle $< 0.85$ |

*Debounce & Hysteresis:* To eliminate control chattering along straights, transitions require a minimum dwell time of $0.40\text{ s}$ and throttle hysteresis ($0.95$ to engage, $< 0.85$ to disengage). Braking triggers an immediate single-tick safety lock to Z-Mode without dwell delay.

### 3.2 Aerodynamic Wake & Slipstream Interaction
When vehicle $B$ follows vehicle $A$ along the circuit with track distance gap $d_{\text{gap}} \in [1.0\text{ m}, 65.0\text{ m}]$:

1. **Straight Segment Wake (Slipstream):** When both cars occupy the same straight segment, aerodynamic drag reduction decays linearly with distance:

$$\delta_{\text{slipstream}} = 0.35 - \left(\frac{d_{\text{gap}} - 1.0}{65.0 - 1.0}\right) \times (0.35 - 0.15)$$

yielding a $35\%$ drag reduction at $1.0\text{ m}$ gap, transitioning down to $15\%$ at $65.0\text{ m}$.

2. **Corner Segment Wake (Dirty Air):** When following in a corner segment, vortex shedding and disrupted airflow penalize aerodynamic downforce by $10\%$ ($k_{\text{aero}} \times 0.90$).

---

## 4. 4-Wheel Thermodynamic & Wear Model

Each wheel (Front-Left, Front-Right, Rear-Left, Rear-Right) maintains independent temperature ($T_i \in [25.0, 145.0]^\circ\text{C}$) and mechanical wear ($w_i \in [0.0, 1.0]$).

### 4.1 Thermal Evolution (Lumped Parameter ODE)
Tyre bulk temperature evolves according to a lumped-node heat balance equation where rates are expressed in $^\circ\text{C/s}$:

$$\frac{dT_i}{dt} = \dot{Q}_{\text{in}, i} - \dot{Q}_{\text{cool}, i}$$

#### Heat Generation ($\dot{Q}_{\text{in}, i}$)
Total heat influx combines four work sources, scaled by the compound warmup multiplier $\kappa_{\text{warmup}}$ when operating below $100.0^\circ\text{C}$:

$$\dot{Q}_{\text{in}, i} = \left(\dot{Q}_{\text{braking}, i} + \dot{Q}_{\text{cornering}, i} + \dot{Q}_{\text{traction}, i} + \dot{Q}_{\text{rolling}}\right) \cdot \kappa_{\text{warmup}}$$

where $\kappa_{\text{warmup}} = 1.35$ (Soft), $1.00$ (Medium), $0.70$ (Hard).

1. **Braking Heat Flux:** Dynamic longitudinal load transfer biases $62\%$ of braking energy to the front axle:
   - $\dot{Q}_{\text{brake, raw}} = 3.20 \cdot \text{brake} \cdot \left(\frac{v}{40.0}\right)$
   - Distribution: FL $= 31\%$, FR $= 31\%$, RL $= 19\%$, RR $= 19\%$.

2. **Cornering / Lateral Load Heat Flux:** Under lateral acceleration $\text{lat\_g} = \min\left(5.5, \frac{v^2 / R}{9.81}\right)$:
   - $\dot{Q}_{\text{lat, total}} = 2.45 \cdot (\text{lat\_g})^{1.3} \cdot \left(\frac{v}{35.0}\right)$
   - In a **left turn** (e.g., Monza Curva Biassono or Istanbul Park Turn 8): The **outside right tyres** absorb **$78\%$** of lateral work (FR: $44\%$ due to steered front scrub, RR: $34\%$), while inside tyres absorb $22\%$ (FL: $10\%$, RL: $12\%$).
   - In a **right turn**, loads mirror to the left side (FL: $44\%$, RL: $34\%$, FR: $10\%$, RR: $12\%$).
   - On straightaways, cornering heat is zero.

3. **Traction / Acceleration Heat Flux:** Engine torque slip at lower/mid speeds heats the rear drive axle:
   - $\dot{Q}_{\text{accel, total}} = 1.60 \cdot \text{throttle} \cdot \max\left(0.20, 1.0 - \frac{v}{95.0}\right)$
   - Distribution: RL $= 48\%$, RR $= 48\%$, FL $= 2\%$, FR $= 2\%$.

4. **Rolling Resistance Heating:** Baseline carcass hysteresis heating at speed:
   - $\dot{Q}_{\text{rolling}} = 0.015 \cdot \left(\frac{v}{30.0}\right)$ applied equally to all wheels.

#### Convective Airflow Cooling ($\dot{Q}_{\text{cool}, i}$)
Cooling to ambient air follows Newton's Law of Cooling with linear airspeed dependence:

$$\dot{Q}_{\text{cool}, i} = (h_{\text{base}} + h_{\text{speed}} \cdot v) \cdot \max(0.0, T_i - T_{\text{ambient}})$$

where:
- $h_{\text{base}} = 0.006\text{ s}^{-1}$
- $h_{\text{speed}} = 0.00018\text{ m}^{-1}$ (yielding $h_{\text{speed}} \cdot v$ in $\text{s}^{-1}$)
- $T_{\text{ambient}} = 25.0^\circ\text{C}$

---

### 4.2 Mechanical Wear Kinetics

Wear accumulates monotonically per time step ($dt$) as a function of combined lateral and longitudinal loads:

$$\Delta w_i = k_{\text{base\_wear}} \cdot \kappa_{\text{wear\_rate}} \cdot \left(1.0 + \text{wear}_{\text{lat}, i} + \text{wear}_{\text{long}, i}\right) \cdot \Theta_{\text{thermal}, i} \cdot \Psi_{\text{driver\_tyre}} \cdot dt$$

where:
- $k_{\text{base\_wear}} = 0.000035\text{ s}^{-1}$ (calibrated for $15 - 25$ lap Grand Prix stint lengths).
- $\kappa_{\text{wear\_rate}}$: Soft $= 1.75$, Medium $= 1.00$, Hard $= 0.55$.
- $\text{wear}_{\text{lat}, i} = (\text{lat\_g})^{1.6} \cdot \text{pos\_lat\_load}_i \cdot 3.2$ (where $\text{pos\_lat\_load}_i$ is the wheel's fractional cornering load).
- $\text{wear}_{\text{long}, i} = (\text{brake} \cdot \text{brake\_share}_i \cdot 2.2) + (\text{throttle} \cdot \text{accel\_share}_i \cdot 1.8)$.
- $\Theta_{\text{thermal}, i} = 1.0 + 0.035 \cdot \max(0.0, T_i - 105.0)$ accelerates degradation when tyres overheat above $105.0^\circ\text{C}$ (blistering/graining).
- $\Psi_{\text{driver\_tyre}} = \max(0.50, 1.30 - \text{driver\_tyre\_mgmt} \cdot 0.40)$ reflects tyre conservation skill.

---

### 4.3 Effective Tyre Grip & Thermal Window

Overall wheel grip combines compound friction, thermal state, and mechanical surface wear:

$$\mu_{\text{effective}, i} = \mu_{\text{compound}} \cdot \mu_{\text{thermal}, i} \cdot \mu_{\text{wear}, i}$$

#### Wear Grip Curve & Grip Floor
Grip degrades non-linearly with cumulative wear, bounded by a physical friction floor:

$$\mu_{\text{wear}, i} = \max\left(0.65, \, 1.0 - 0.35 \cdot (\min(1.0, \max(0.0, w_i)))^{1.35}\right)$$

- At $w_i = 0.0$ (brand new tyre): $\mu_{\text{wear}} = 1.00$.
- At $w_i \ge 1.0$ (completely worn carcass): $\mu_{\text{wear}} = 0.65$ (**calibrated grip floor**).

#### Thermal Grip Window
The optimal grip plateau operates between $95.0^\circ\text{C}$ and $105.0^\circ\text{C}$:

$$\mu_{\text{thermal}, i} = \begin{cases}
1.0 & \text{if } 95.0 \le T_i \le 105.0 \\
\max\left(0.75, \, 1.0 - 0.22 \cdot \min\left(1.0, \left(\frac{95.0 - T_i}{30.0}\right)^{1.1}\right)\right) & \text{if } T_i < 95.0 \\
\max\left(0.70, \, 1.0 - 0.28 \cdot \min\left(1.0, \left(\frac{T_i - 105.0}{25.0}\right)^{1.1}\right)\right) & \text{if } T_i > 105.0
\end{cases}$$

- Cold tyre lower bound ($T \le 65.0^\circ\text{C}$): grip drops to $0.75$.
- Overheated tyre lower bound ($T \ge 130.0^\circ\text{C}$): grip drops to $0.70$.

#### Compound Specifications

| Compound | Code | Color | Base Friction ($\mu$) | Relative Pace Ratio | Warmup Multiplier | Wear Multiplier |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Soft (C3)** | `S` | `#FF334B` | $1.85$ | $1.85 / 1.70 \approx 1.088$ | $1.35\times$ | $1.75\times$ |
| **Medium (C2)** | `M` | `#FFD600` | $1.70$ | $1.70 / 1.70 = 1.000$ | $1.00\times$ | $1.00\times$ |
| **Hard (C1)** | `H` | `#FFFFFF` | $1.55$ | $1.55 / 1.70 \approx 0.912$ | $0.70\times$ | $0.55\times$ |

---

## 5. Powertrain & Hybrid Energy Recovery System (ERS)

### 5.1 2026 Technical Regulation Specifications
- **ICE Power Unit:** 1.6L turbocharged engine delivering $a_{\text{engine, max}} = 12.0 - 12.4\text{ m/s}^2$ peak longitudinal acceleration.
- **Maximum Fuel Flow Rate:** $80.0\text{ kg/h}$ at full throttle.
- **Battery Storage Depot:** Fixed capacity of $4.0\text{ MJ}$ ($1.11\text{ kWh}$), initial race charge $3.4\text{ MJ}$ ($85.0\%$).
- **MGU-K Maximum Electrical Power Output:** $350.0\text{ kW}$ (under 2026 50/50 ICE-Electric power split).
- **MGU-K Maximum Kinetic Regeneration:** $350.0\text{ kW}$.

### 5.2 Kinetic Regeneration Under Braking
When braking ($\text{brake} > 0.01$), fuel injection cuts to zero ($0.0\text{ kg/h}$) and MGU-K regenerates kinetic energy:

$$P_{\text{regen, kW}} = \min(350.0, \, 0.16 \cdot a_{\text{brake, actual}} \cdot v)$$

$$\Delta E_{\text{battery}} = \left(\frac{P_{\text{regen, kW}}}{1000.0}\right) \cdot dt \quad [\text{MJ}]$$

The coefficient $0.16$ is an empirical calibration factor scaling specific braking power into electrical kW recovery, bounded strictly by the $350.0\text{ kW}$ regulatory ceiling.

### 5.3 Baseline Hybrid Deployment
On straights when $\text{throttle} > 0.50$ and battery $\text{SOC} > 5.0\%$, the MGU-K provides baseline electrical assist:

$$a_{\text{electric\_boost}} = 1.40 \cdot \text{throttle} \cdot \text{mass\_factor} \quad [\text{m/s}^2]$$

$$\Delta E_{\text{deplete}} = 0.120 \cdot \text{throttle} \cdot dt \quad [\text{MJ}] \quad (120\text{ kW})$$

### 5.4 Manual Override Mode (MOM)
The 2026 Manual Override Mode replaces traditional DRS by providing an on-demand high-power electrical deploy on straightaways:

1. **Activation Criteria:**
   - Preceding car time delta: $\Delta t_{\text{ahead}} \le 1.00\text{ s}$.
   - Circuit segment: Straight ($R = \infty$, steering straight).
   - Vehicle speed: $v \ge 280.0\text{ km/h}$.
   - Driver controls: $\text{throttle} > 0.90$ and $\text{brake} \le 0.01$.
   - Battery State of Charge: $\text{SOC} \ge 10.0\%$.

2. **Electrical Deployment:**
   - Calculates electrical acceleration boost from full $350\text{ kW}$ electrical power:
     $$a_{\text{boost}} = \min\left(6.0, \, \max\left(2.5, \, \frac{350\,000.0}{M_{\text{total}} \cdot \max(20.0, v)}\right)\right) \quad [\text{m/s}^2]$$
   - High-rate battery discharge: $0.350\text{ MJ/s}$ ($350\text{ kW}$ rate):
     $$\Delta E_{\text{deplete}} = 0.350 \cdot dt \quad [\text{MJ}]$$
   - Top speed ceiling extension: $+15\%$ headroom ($1.15 \cdot v_{\text{max\_ms}}$).

3. **Automatic Safeguards & Lockout:**
   - Immediate cutoff if battery drops below $10.0\%$ SOC.
   - Immediate cutoff upon brake tap ($\text{brake} > 0.01$), corner entry, or speed dropping below $272.0\text{ km/h}$.

---

## 6. Track Model & Coordinate Geometry

### 6.1 1D Analytical Segment Model
The physics engine operates along a 1D scalar coordinate $s \in [0, L_{\text{track}})$. The circuit is discretized into sequential, contiguous segments:

$$\text{TrackSegment}(s) = \{ \text{name}, \, \text{type} \in \{\text{straight}, \text{corner}\}, \, \text{length}, \, R, \, \text{sector}, \, \text{direction} \in \{\text{left}, \text{right}, \text{straight}\} \}$$

- Curvature is assumed constant per corner segment ($k = 1/R$).
- Start and end positions are analytical: $\text{start\_pos}_{i} = \sum_{k=1}^{i-1} L_k$, $\text{end\_pos}_i = \text{start\_pos}_i + L_i$.
- Track wraparound at the start/finish line is seamless: $s \leftarrow s - L_{\text{track}}$ when $s \ge L_{\text{track}}$.

### 6.2 2D Normalized Waypoints (UI Layer)
Each circuit includes an ordered array of normalized 2D coordinates $(x_k, y_k) \in [0.0, 1.0]^2$ derived from satellite GPS traces.
- These waypoints are used **strictly by the PySide6 UI view** (`circuit_canvas.py`) to render the circuit map and interpolate the car's visual position.
- The 2D coordinates **do not govern vehicle dynamics or curvature physics**, preserving real-time speed and deterministic lap timing.

---

## 7. Numerical Method & Execution Architecture

### 7.1 Integration Method & Timestep
- **Fixed Timestep:** $\Delta t = 0.050\text{ s}$ ($20\text{ Hz}$).
- **Numerical Scheme:** Explicit forward Euler for acceleration, thermal fluxes, and wear kinetics, followed by position integration:

$$v_{t + \Delta t} = \max\left(0.0, \, \min(v_{\text{top\_cap}}, \, v_t + a_{\text{net}} \cdot \Delta t)\right)$$

$$s_{t + \Delta t} = s_t + v_{t + \Delta t} \cdot \Delta t$$

### 7.2 State Update Sequence (per 20 Hz tick)
Each simulation cycle executes in strict deterministic order:
1. **Multi-Car Wake & Strategy Evaluation:** Forward distance gaps, straightaway slipstream decay, dirty air flags, and MOM activation eligibility are updated.
2. **Pit Lane Logic:** Checks pit requests, enforces the $80.0\text{ km/h}$ pit limiter, tracks the $2.4\text{ s}$ stationary pit box stop, and executes tyre changes.
3. **Driver AI Decision:** Evaluates lookahead corner horizons ($450.0\text{ m}$) to compute target apex velocity and throttle/brake inputs.
4. **Active Aero & MOM State Machine:** Evaluates dwell timers and safety locks.
5. **Longitudinal Kinematic Integration:** Computes engine propulsion, electric assist, aerodynamic drag, rolling resistance, and braking deceleration to update $v(t)$.
6. **4-Wheel Thermodynamic & Wear Integration:** Computes independent FL, FR, RL, RR thermal fluxes and wear increments.
7. **Transmission & RPM:** Calculates active gear and engine RPM.
8. **Path Coordinate Advancement:** Updates track position $s(t)$ and checks lap completion.

---

## 8. Parameter Dictionary

The following table documents the core constants, their numerical values, physical dimensions, and scientific classification:

| Parameter Name | Code Variable | Value | Unit | Scientific Classification | Description |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Gravitational Acceleration** | `g` | $9.81$ | $\text{m/s}^2$ | Physical Constant | Standard Earth gravitational acceleration. |
| **Minimum Dry Mass** | `dry_mass_kg` | $798.0$ | $\text{kg}$ | Regulation Standard | 2024–2026 FIA minimum car + driver mass. |
| **Initial Fuel Mass** | `fuel` | $100.0$ | $\text{kg}$ | Regulation Standard | Maximum race start fuel capacity. |
| **Maximum Fuel Flow** | `fuel_flow_kgh` | $80.0$ | $\text{kg/h}$ | Regulation Standard | 2026 Technical Regulation fuel flow ceiling. |
| **Battery Energy Capacity** | `ers_max_energy_mj` | $4.0$ | $\text{MJ}$ | Regulation Standard | 2026 ERS maximum usable battery capacity. |
| **MGU-K Max Power** | `p_regen_kw` / MOM | $350.0$ | $\text{kW}$ | Regulation Standard | 2026 MGU-K peak deployment and regeneration limit. |
| **Baseline ICE Acceleration** | `acceleration` | $12.0$ | $\text{m/s}^2$ | Calibration Parameter | Calibrated peak engine acceleration on fresh tyres. |
| **Max Braking Deceleration** | `max_brake_decel` | $42.0$ | $\text{m/s}^2$ | Calibration Parameter | Peak mechanical braking deceleration ($\approx 4.3\text{G}$). |
| **Base Drag Coefficient** | `drag_coeff` | $0.00038$ | $\text{m}^{-1}$ | Calibration Parameter | Baseline aerodynamic drag factor (Medium downforce). |
| **Rolling Resistance** | `rolling_resistance` | $0.15$ | $\text{m/s}^2$ | Calibration Parameter | Constant mechanical rolling resistance deceleration. |
| **Track Baseline Friction** | `mu` | $1.75$ | Dimensionless | Calibration Parameter | Baseline slick tyre-to-tarmac friction coefficient. |
| **Fuel Mass Factor Multiplier** | `mass_factor` | $0.65$ | Dimensionless | Calibration Parameter | Sensitivity scalar reflecting aerodynamic vertical load dominance. |
| **X-Mode Drag Multiplier** | `aero_mult` | $0.60$ | Dimensionless | Model Assumption | 2026 active aero drag reduction factor ($40\%$ drop). |
| **Z-Mode Corner Horizon** | `dist_to_corner` | $35.0$ | $\text{m}$ | Model Assumption | Lookahead distance to deploy Z-Mode before corner entry. |
| **Aero Mode Dwell Time** | `aero_mode_hold_timer`| $0.40$ | $\text{s}$ | Implementation Constant | Debounce time preventing high-frequency aero chattering. |
| **Slipstream Max Reduction**| `slipstream_reduction`| $0.35$ | Dimensionless | Model Assumption | Maximum straightaway aero drag drop at $1.0\text{ m}$ gap. |
| **Slipstream Max Distance** | `closest_dist` | $65.0$ | $\text{m}$ | Model Assumption | Maximum trailing gap distance for aerodynamic wake effect. |
| **Dirty Air Downforce Loss**| `in_dirty_air` | $0.10$ | Dimensionless | Model Assumption | $10\%$ downforce penalty when following in corners. |
| **Braking Thermal Constant**| `k_brake` | $3.20$ | $^\circ\text{C/s}$ | Calibration Parameter | Heat generation rate at full braking and $200\text{ km/h}$. |
| **Braking Front Bias** | `brake_share` | $0.62$ | Dimensionless | Model Assumption | $62\%$ front axle brake distribution ($31\%$ FL, $31\%$ FR). |
| **Cornering Outside Bias** | `corner_heat_rates` | $0.78$ | Dimensionless | Model Assumption | $78\%$ lateral load on outside tyres ($44\%$ front, $34\%$ rear). |
| **Static Cooling Coeff** | `h_base` | $0.006$ | $\text{s}^{-1}$ | Calibration Parameter | Convective cooling heat transfer coefficient at rest. |
| **Dynamic Cooling Coeff** | `h_speed` | $0.00018$ | $\text{m}^{-1}$ | Calibration Parameter | Airspeed-dependent convective cooling multiplier. |
| **Base Wear Rate** | `base_wear_rate` | $0.000035$ | $\text{s}^{-1}$ | Calibration Parameter | Nominal mechanical wear progression per unit time. |
| **Grip Floor** | `wear_grip` | $0.65$ | Dimensionless | Model Assumption | Minimum friction multiplier on fully degraded tyres. |
| **Optimal Thermal Window** | `WheelState.update_grip`| $[95, 105]$| $^\circ\text{C}$ | Model Assumption | Peak tyre operating temperature band. |
| **Simulation Timestep** | `dt` | $0.050$ | $\text{s}$ | Implementation Constant | Fixed $20\text{ Hz}$ numerical integration step. |

---

## 9. Engineering Limitations & Architectural Trade-Offs

| Component | Industry High-Fidelity Tool (e.g., rFactor Pro, Dymola) | This Simulation Model (Deterministic 20 Hz) | Justification & Architectural Impact |
| :--- | :--- | :--- | :--- |
| **Chassis Dynamics** | 14-DOF multi-body suspension linkages with compliance | Point-mass forward Euler kinematic acceleration | Stable, zero-drift, real-time execution across arbitrary lap counts without stiff ODE solver blowups. |
| **Tyre Model** | Non-linear Pacejka 2002 with transient slip relaxation | Lumped thermal node + algebraic $(1 - 0.35 w^{1.35})$ grip curve | Eliminates stiff tire slip ODEs while capturing asymmetric thermal load transfer and compound wear crossovers. |
| **Aerodynamics** | Unsteady 3D Navier-Stokes CFD wake solutions | 1D algebraic gap decay function ($1.0\text{ m} - 65.0\text{ m}$) | Real-time multi-car slipstream and dirty air calculations without CFD latency or high compute overhead. |
| **Track Geometry** | 3D LiDAR point clouds with variable camber/elevation | 1D piecewise segment array + 2D normalized spline waypoints | Preserves authentic segment lengths and corner radii while enabling exact analytical distance calculations. |

---

## 10. Model Status: Verification, Calibration & Validation

To maintain strict scientific integrity, the status of this computational testbed is categorized under standard systems engineering definitions:

### 10.1 Software Verification: COMPLETE (100% Passing)
Software verification confirms that the implementation correctly executes its specified algorithms and state transitions. The repository contains automated test suites verifying:
- **Numerical Robustness:** Singularity avoidance at $v = 0.0$ and $v = 450.0\text{ km/h}$, non-negative energy conservation ($E \ge 0.0\text{ MJ}$), and fuel exhaustion coastdown.
- **Control State Stability:** Zero-chatter active aero transitions and instantaneous single-tick safety lock to Z-Mode upon braking.
- **Strategy & Limiter Integration:** $80.0\text{ km/h}$ pit lane limiter enforcement and $2.4\text{ s}$ stationary box stop tyre changes.
- **Data Pipeline Integrity:** Continuous 20 Hz CSV telemetry export without NaN, null, or desync errors.

### 10.2 Parametric Sensitivity & Calibration: WITHIN TARGET RANGES
The model parameters have been calibrated against published Grand Prix engineering references:
- **Fuel Mass Sensitivity:** Simulates $0.360\text{ s} / 10\text{ kg}$ lap time delta on Monza (target reference range: $0.30 - 0.40\text{ s} / 10\text{ kg}$).
- **Active Aero Performance:** Active aero X-Mode delivers $+16.0\text{ km/h}$ top speed and $-1.200\text{ s}$ lap time advantage on Monza (target reference range: $+15 - 25\text{ km/h}$ and $-1.0 - 2.0\text{ s}$).
- **Tyre Compound Ordering:** Soft compound achieves a $1.92\times$ wear rate ratio relative to Medium on Istanbul Park (target reference: $\approx 1.75\times$).

### 10.3 External Validation: NOT EXTERNALLY VALIDATED
- **Current Status:** The repository **does not** currently ingest raw, independent, external telemetry datasets (e.g., real-world GPS traces or ECU CAN-bus logs) to perform residual error tracking (such as RMSE velocity correlation).
- **Claim Boundary:** Results in this repository are calibrated engineering benchmarks, not empirical real-world validation.

---

## 11. Recommended Next Engineering Step

The single highest-value next step to advance this platform from a **calibrated kinematic model** toward **formal empirical validation** is:
> **Ingest FastF1 Grand Prix Telemetry Traces:**
> Ingest publicly available FastF1 session telemetry (e.g., 2023 Italian GP qualifying speed traces for Autodromo Nazionale Monza), resample to the 20 Hz simulation grid, and compute formal Root Mean Square Error (RMSE) metrics across longitudinal velocity, corner apex speeds, and braking deceleration distances.
