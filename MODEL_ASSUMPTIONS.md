# Motorsport Simulation — Mathematical Model Assumptions, Formulations & Engineering Limitations

**Version:** 1.0  
**Domain:** Vehicle Dynamics, 2026 FIA Technical Regulations, Telemetry Data Engineering  
**Scope:** Kinematic Integration, Longitudinal/Lateral Vehicle Dynamics, 4-Wheel Thermal Kinetics, Dynamic Race Strategy  

---

## 1. Executive Summary

This simulation is engineered as a **deterministic, segment-based, 20 Hz kinematic and telemetry testbed** designed to evaluate race strategy, active aerodynamics (2026 FIA Regulations), energy management, and tyre degradation. 

It is **explicitly not a full multi-body, aero-elastic, 6-DOF dynamic simulator** (such as rFactor Pro, Vi-grade, or Dymola). Instead, it adopts continuous numerical formulations and point-mass kinematic approximations calibrated against empirical Formula 1 telemetry. This architectural decision guarantees:
- **100% Deterministic Reproducibility:** Identical initial conditions and driver traits yield identical multi-lap trajectories.
- **Real-Time 20 Hz Simulation Loop:** Decoupled Model-View-ViewModel (MVVM) architecture capable of zero-lag UI rendering alongside background data pipelines.
- **Physical Defensibility:** Core parameters, energy limits, deceleration bounds, and mass sensitivities strictly align with modern and upcoming Grand Prix technical standards.

---

## 2. Vehicle Dynamics & Kinematic Formulations

### 2.1 Longitudinal Dynamics
The longitudinal acceleration of the vehicle along the circuit tangent is governed by Newton's Second Law:

$$M_{\text{total}}(t) \cdot \frac{dv}{dt} = F_{\text{propulsion}} - F_{\text{drag}} - F_{\text{rolling}} - F_{\text{braking}}$$

#### Aerodynamic Drag ($F_{\text{drag}}$)
Aero drag follows the classical quadratic velocity relationship:

$$F_{\text{drag}} = \frac{1}{2} \rho C_d A v^2$$

In the discrete simulation implementation, this is parameterized into an effective drag coefficient $k_{\text{drag}}$:

$$a_{\text{drag}} = k_{\text{drag}} \cdot v^2 \quad \text{where} \quad k_{\text{drag}} = k_{\text{base}} \cdot \gamma_{\text{aero}} \cdot (1 - \delta_{\text{slipstream}})$$

- $k_{\text{base}} = 0.00038\text{ m}^{-1}$ (calibrated for high-downforce open-wheel geometry).
- $\gamma_{\text{aero}} = 0.60$ in **X-Mode** (40% drag reduction on straights) and $1.00$ in **Z-Mode**.
- $\delta_{\text{slipstream}} \in [0.15, 0.35]$ when operating in the aerodynamic wake of a leading car.

#### Rolling Resistance ($F_{\text{rolling}}$)
Mechanical resistance from tyre carcass deformation and drivetrain friction is modeled as constant deceleration:

$$a_{\text{rolling}} = C_{rr} \cdot g \approx 0.15\text{ m/s}^2$$

#### Dynamic Mass Scaling ($M_{\text{total}}$)
Vehicle mass evolves dynamically with instantaneous fuel load:

$$M_{\text{total}}(t) = M_{\text{dry}} + M_{\text{fuel}}(t)$$

- Minimum dry weight + driver: $M_{\text{dry}} = 798.0\text{ kg}$ (FIA Regulation standard).
- Initial fuel capacity: $M_{\text{fuel}}(0) = 100.0\text{ kg}$.
- In Formula 1, aerodynamic downforce at high speed ($F_z > 25\text{ kN}$) substantially decouples total normal load from fuel mass. To reflect the empirical Grand Prix benchmark ($\approx 0.30 - 0.40\text{ s} / 10\text{ kg}$ lap time delta), inertial acceleration and braking scale via the mass factor:

$$\text{mass\_factor} = \frac{M_{\text{dry}} + 10.0}{M_{\text{dry}} + 10.0 + \Delta M_{\text{fuel}} \cdot 0.50}$$

### 2.2 Lateral Dynamics & Cornering
Cornering capability is modeled using a point-mass approximation balancing centripetal acceleration against tyre lateral grip and aerodynamic downforce:

$$a_{\text{lateral}} = \frac{v^2}{R} \le \mu_{\text{effective}} \cdot g$$

The maximum allowable apex velocity for a corner of radius $R$ is formulated as:

$$v_{\text{apex}} = \sqrt{\mu_{\text{base}} \cdot g \cdot R} \cdot k_{\text{compound}} \cdot k_{\text{thermal}} \cdot k_{\text{wear}} \cdot k_{\text{aero}} \cdot \Psi_{\text{driver}}$$

- $\mu_{\text{base}}$: Circuit baseline friction coefficient (typically $1.65 - 1.85$).
- $k_{\text{aero}}$: Downforce package factor ($1.08$ for High-Downforce, $1.00$ for Medium, $0.94$ for Low-Downforce Monza trim).
- In dirty air ($d_{\text{gap}} \le 65\text{ m}$ in cornering segments), downforce is penalized by $10\%$ ($k_{\text{aero}} \times 0.90$).

### 2.3 Braking Deceleration Calibration ($42\text{ m/s}^2 \approx 4.3\text{G}$)
The maximum calibrated braking deceleration is set to $42.0\text{ m/s}^2$:
- **Physical Justification:** Modern Formula 1 carbon-carbon brake discs (operating at $600^\circ\text{C} - 1000^\circ\text{C}$) paired with peak aerodynamic downforce generate over $4.5\text{G} - 5.0\text{G}$ of longitudinal deceleration at high entry speeds ($> 320\text{ km/h}$).
- **Kinematic Braking Point Trigger:** The autonomous driving agent evaluates upcoming corner horizons ($450\text{ m}$) and initiates braking based on:

$$d_{\text{brake}} = \frac{v_{\text{current}}^2 - v_{\text{target}}^2}{2 \cdot a_{\text{brake, effective}}} \cdot \eta_{\text{driver\_skill}}$$

where $\eta_{\text{driver\_skill}} = 1.04 - (\text{skill} - 0.8) \times 0.08$ allows elite drivers to brake deeper into apexes.

### 2.4 Assumptions vs. Real-World Limitations
1. **No 6-DOF Multi-Body Suspension:** The chassis does not simulate transient pitch (brake dive), roll (anti-roll bar stiffness), or heave (third damper oscillation).
2. **Point-Mass Kinematics:** Yaw moment of inertia and slip angles ($\alpha$) are omitted in favor of segment-wise apex velocity limits and cumulative path integration.

---

## 3. Aerodynamics & 2026 Technical Regulations

| Parameter | Z-Mode (Cornering / Braking) | X-Mode (High-Speed Straight) |
| :--- | :--- | :--- |
| **Wing State** | High Downforce (Standard AoA) | Low Drag (Flaps opened / neutral) |
| **Drag Multiplier ($\gamma$)** | $1.00$ (Baseline Drag) | $0.60$ (**40% Drag Reduction**) |
| **Deployment Trigger** | Automatic in corners, braking, or $d_{\text{corner}} \le 35\text{ m}$ | Automatic on straights when steering angle $\approx 0^\circ$ and throttle $> 95\%$ |
| **Top Speed Headroom** | Baseline ($315 - 325\text{ km/h}$) | $+5\%$ aerodynamic top speed extension |

### Aerodynamic Wake & Slipstream
When car $B$ trails car $A$ along the track centerline with gap distance $d_{\text{gap}} \in [1.0\text{ m}, 65.0\text{ m}]$:
1. **On Straights (Slipstream / Tow):** Aero drag is reduced linearly from $35\%$ at $1.0\text{ m}$ to $15\%$ at $65.0\text{ m}$:

$$\delta_{\text{drag}} = 0.35 - \left(\frac{d_{\text{gap}} - 1.0}{65.0 - 1.0}\right) \times (0.35 - 0.15)$$

2. **In Corners (Dirty Air):** Vortex shedding and disturbed boundary layers disrupt front wing and underfloor Venturi suction, applying a **$10\%$ downforce penalty** to the trailing vehicle.

---

## 4. 4-Wheel Thermodynamic & Wear Model

Each wheel (Front-Left, Front-Right, Rear-Left, Rear-Right) maintains independent temperature ($T$) and surface wear ($w \in [0.0, 1.0]$).

### 4.1 Thermal Energy Conservation
Tyre bulk temperature evolves according to heat flux equilibrium:

$$\frac{dT_i}{dt} = \dot{Q}_{\text{in}, i} - \dot{Q}_{\text{cool}, i}$$

#### Heat Generation ($\dot{Q}_{\text{in}}$)
Heat is generated by three physical work sources:

$$\dot{Q}_{\text{in}, i} = \dot{Q}_{\text{braking}, i} + \dot{Q}_{\text{cornering}, i} + \dot{Q}_{\text{traction}, i}$$

1. **Braking Heat Flux:** Dynamic weight transfer biases $62\%$ of braking energy to front tyres (FL/FR: $31\%$ each, RL/RR: $19\%$ each).
2. **Lateral Load Transfer in Cornering:** Under lateral acceleration, centrifugal forces transfer normal load to the outside tyres. For turn direction $D \in \{\text{left}, \text{right}\}$:
   - In a **left turn** (e.g., Monza Curva Grande or Istanbul Park Turn 8): **Right tyres (FR & RR)** absorb $65\%$ of cornering friction work, while inside tyres (FL & RL) absorb $35\%$.
   - The severity scales inversely with corner radius: $k_{\text{lateral}} \propto \frac{1}{\sqrt{R}}$.
3. **Traction Heat Flux:** Rear-axle longitudinal slip during acceleration heats RL and RR ($50\%$ each).

#### Convective Cooling ($\dot{Q}_{\text{cool}}$)
Cooling from freestream airflow is modeled via Newton's Law of Cooling with velocity dependence:

$$\dot{Q}_{\text{cool}, i} = (h_{\text{static}} + h_{\text{dynamic}} \cdot v) \cdot (T_i - T_{\text{ambient}})$$

- $h_{\text{static}} = 0.040\text{ s}^{-1}$
- $h_{\text{dynamic}} = 0.0016\text{ m}^{-1}$
- $T_{\text{ambient}} = 25.0^\circ\text{C}$

### 4.2 Mechanical Wear Kinetics
Wear rate per time step is non-linear and coupled to thermal stress:

$$\Delta w_i = \left(\frac{v}{80.0}\right) \cdot \left[ k_{\text{lat}} \cdot \left(\frac{80.0}{R}\right) + k_{\text{brake}} \cdot \text{brake} \right] \cdot \kappa_{\text{compound}} \cdot \Theta_{\text{thermal}} \cdot (1.0 - \text{skill} \cdot 0.18) \cdot dt$$

Effective mechanical grip follows a power law with a physical grip floor:

$$\mu_{\text{effective}} = \mu_{\text{compound}} \cdot \mu_{\text{thermal}} \cdot \left[ 0.35 + 0.65 \cdot (1.0 - \min(1.0, w))^{1.3} \right]$$

- Optimal thermal window: $[80^\circ\text{C}, 105^\circ\text{C}]$. Below $70^\circ\text{C}$ (cold tyres) or above $115^\circ\text{C}$ (overheating blister), thermal grip $\mu_{\text{thermal}}$ drops toward $0.78$.

### 4.3 Assumptions vs. Real-World Limitations
- **Omission of Pacejka '96 Brush Model:** Transient slip angles ($\alpha$), longitudinal slip ratio ($\kappa$), and camber thrust are synthesized into deterministic grip multipliers.
- **Thermal Uniformity:** The tyre is modeled as a single lumped thermal node rather than distinct carcass, tread surface, and inner air cavity temperatures.

---

## 5. Powertrain & 4.0 MJ Hybrid Energy Recovery System (ERS)

### 5.1 2026 FIA Regulation Boundaries
- **ICE Power Unit:** 1.6L turbocharged internal combustion engine delivering baseline longitudinal acceleration ($a \approx 12.0 - 12.4\text{ m/s}^2$).
- **Maximum Fuel Flow:** $80.0\text{ kg/h}$ at full throttle.
- **Battery Storage Depot:** Fixed capacity of $4.0\text{ MJ}$.
- **MGU-K Maximum Power Output:** $350.0\text{ kW}$ (electrical assist).
- **MGU-K Maximum Regeneration:** $350.0\text{ kW}$ (kinetic braking recovery).

### 5.2 Kinetic Regeneration Under Braking
When braking ($\text{brake} > 0.01$), fuel injection cuts off ($0.0\text{ kg/h}$) and MGU-K regenerates kinetic energy:

$$P_{\text{regen}} = \min\left(350.0\text{ kW}, \,\, 0.16 \cdot a_{\text{brake}} \cdot v\right)$$

$$\Delta E_{\text{battery}} = \left(\frac{P_{\text{regen}}}{1000.0}\right) \cdot dt$$

### 5.3 Manual Override Mode (MOM)
The 2026 Manual Override Mode replaces traditional DRS by providing additional high-power electrical deploy on straights:
1. **Activation Criteria:**
   - Preceding car within detection gap: $\Delta t_{\text{ahead}} \le 1.0\text{ s}$.
   - Circuit location: Straight segment ($R = \infty$, steering straight).
   - Vehicle speed: $v \ge 280.0\text{ km/h}$.
   - Battery State of Charge: $\text{SOC} \ge 10.0\%$.
2. **Electrical Deployment:**
   - Deploys full $350\text{ kW}$ boost: $a_{\text{boost}} = \frac{350\,000}{M_{\text{total}} \cdot v}$ ($2.5 - 6.0\text{ m/s}^2$).
   - Battery discharge rate: $0.350\text{ MJ/s}$.
   - Extends top speed ceiling by $+15\%$.
3. **Automatic Safeguards:**
   - Deactivates immediately if battery drops below $10.0\%$ SOC.
   - Deactivates immediately upon braking, corner entry, or entering the pit lane limiter.

---

## 6. Summary of Engineering Trade-Offs

| Component | Industry Reality (High-Fidelity) | Simulation Model (Deterministic 20 Hz) | Justification / Engineering Impact |
| :--- | :--- | :--- | :--- |
| **Track Coordinates** | 3D LiDAR point clouds with elevation/camber | 2D Catmull-Rom spline with arc lengths & curvature | Preserves true layout geometry while maintaining analytical distance calculation. |
| **Tyre Model** | Non-linear Pacejka 2002 with thermal/pressure dynamics | Lumped thermal node + $(1 - w)^{1.3}$ wear penalty | Real-time 20 Hz calculation without stiff ODE solver overhead. |
| **Aero Interaction** | Unsteady 3D CFD wake Navier-Stokes | Empirical 1D gap decay function ($1\text{m} - 65\text{m}$) | Deterministic computation without CFD latency. |
| **Chassis State** | 14-DOF multi-body suspension linkages | Point-mass forward Euler kinematic integration | Stable, drift-free execution across arbitrary simulation durations. |
