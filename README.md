# PID Control from Scratch

A PID controller for a mass–spring–damper, written from zero in NumPy and Matplotlib
(no control libraries). Made for the Modern Monk Labs Physical AI intern assignment.

**Plant:** m·x'' + c·x' + k·x = u, with m = 1 kg, c = 10 N·s/m, k = 20 N/m.
**Goal:** move the mass to 1 m with a 30 N motor limit and ±1 mm sensor noise.

## Result

Final gains: **Kp = 150, Ki = 300, Kd = 15**,
with clamping anti-windup, a filtered derivative (τ = 20 ms) and derivative on measurement.

![Final design](figures/fig14_final.png)

| Rise time | Overshoot | Settling time (2%) | Force noise | Steady-state error |
|---|---|---|---|---|
| 0.464 s | 0.22 % | 0.794 s | 0.52 N | 0 |

My targets were overshoot < 2 %, settling < 1 s and force noise < 1 N.
I chose these gains as a balance between motor wear (low force noise) and robustness:
they still meet every target with a 2 kg load, and when pushed past their limits
(e.g. a 100 ms controller update) they degrade gently instead of oscillating.
The full reasoning is in the report.

## Approach

1. Simulated the plant from its equation (semi-implicit Euler, 1 ms steps) and checked it against the force balance (20 N holds 1 m).
2. Wrote the PID class from scratch and measured every result with the same four metrics (rise, overshoot, settling, steady-state error).
3. Tested P, I and D one at a time and checked each against theory: P-only final position and overshoot match the formulas to within 0.1 %.
4. Added the real-world problems one by one (30 N motor limit, ±1 mm sensor noise, sudden target jumps, slow controller updates), showed each failure, then fixed it.
5. Chose final gains against explicit targets with every problem switched on, then stress-tested them (heavier mass, weaker motor, slower updates).
6. Applied Ziegler–Nichols to a second system, 1/(s+1)³, and improved the result by hand.

## What worked, what didn't, what next

**What worked**
- The simulation agrees with the theory: `checks.py` confirms 11 predictions automatically.
- Each fix worked as predicted: anti-windup cut overshoot from 24 % to 0 %, the D filter cut force noise from 25.3 N to 1.0 N, and D on measurement cut the target-jump spike from 30 300 N to 300 N.
- The final gains meet all targets and still do with a 2 kg load.

**What didn't**
- No gains can meet the targets when the physics forbids it: with a 5 kg mass, a 15 N motor, or a 2 m target, the motor simply lacks the force (force balance, not tuning).
- The Ziegler–Nichols recipe alone gave 52 % overshoot; it needed three hand adjustments to reach 1 %.
- The D filter is a trade-off: more smoothing means less noise but a slower reaction; I chose τ = 20 ms as the balance.
- The model is idealised: linear spring, no friction, no motor dynamics, and uniform sensor noise. Real hardware would need retuning.

**What I would explore next**
- Disturbance rejection: push the block with 10 N mid-run and measure how quickly PID recovers.
- Feedforward: send the known 20 N directly, so PID only corrects the remaining error.
- Automatic gain search: optimise the gains against the targets instead of comparing candidates by hand.
- Show how the system's poles move as the gains change, to explain stability visually.
- An interactive slider tool to change gains and watch the response live.
- Run the same controller on real hardware (e.g. a DC motor with an encoder on a microcontroller).

## Quick start

    git clone https://github.com/Sannidhi20040/pid-control-from-scratch.git
    cd pid-control-from-scratch
    python3 -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate
    pip install -r requirements.txt

    python checks.py                 # 11 checks: simulation vs theory, all should PASS
    python make_figures.py           # regenerates every figure into figures/

To reproduce the tables in the report:

    python sweep.py                  # P sweep vs formulas, P/PI/PD/PID, real-world problems
    python zn.py                     # Ziegler–Nichols: finds Ku and Tu, then the recipe gains
    python tune.py                   # candidate gains vs targets, stress test of the final choice

The sensor noise uses a fixed random seed, so everyone gets identical graphs and numbers.

## Files

| File | What it does |
|---|---|
| `plant.py` | Simulates the mass–spring–damper (semi-implicit Euler, dt = 1 ms), plus the 1/(s+1)³ system |
| `pid.py` | The PID class: limits, clamping anti-windup, derivative filter, derivative on measurement |
| `metrics.py` | Rise time, overshoot, settling time and steady-state error from a response |
| `sweep.py` | Prints the tables: P sweep vs formulas, P/PI/PD/PID, windup, noise, kick, update rate |
| `zn.py` | Ziegler–Nichols: searches for Ku, measures Tu on 1/(s+1)³ and computes the ZN gains |
| `tune.py` | Compares candidate gains against my targets and stress-tests the final choice |
| `checks.py` | Automatic checks that the simulation agrees with the formulas |
| `make_figures.py` | Draws every figure and diagram in the report |

## Figures

`python make_figures.py` saves all 16 into `figures/`.

| File | Shows | Report section |
|---|---|---|
| `fig00_loop.png` | The feedback loop: target → controller → plant → sensor | 1 |
| `fig00b_block.png` | The test system and the forces on the block | 3 |
| `fig01_open_loop.png` | Open-loop response (constant 20 N, no controller) | 3 |
| `fig02_metrics.png` | The four performance measures marked on one response | 4 |
| `fig03_p_sweep.png` | P only at several gains: always stops short of the target | 5 |
| `fig04_pi.png` | Adding I: the remaining error goes to zero | 5 |
| `fig05_pd.png` | Adding D: overshoot damped | 5 |
| `fig06_compare.png` | P vs PI vs PD vs PID | 6 |
| `fig07_parts.png` | The P, I and D forces over time | 6 |
| `fig08_windup.png` | Integral windup at 30 N, fixed by anti-windup | 7a |
| `fig09_noise.png` | ±1 mm sensor noise makes D jumpy, fixed by a filter | 7b |
| `fig10_kick.png` | Derivative kick, fixed by derivative on measurement | 7c |
| `fig11_period.png` | Effect of a slower controller update | 7d |
| `fig12_ku.png` | Raising P on 1/(s+1)³ until it swings steadily (Ku, Tu) | 8 |
| `fig13_zn.png` | Ziegler–Nichols gains, then improved by hand | 8 |
| `fig14_final.png` | Final design with every real-world problem switched on | 6, 9 |

## Checks

`checks.py` verifies, among others:
- P-only final position equals Kp/(k+Kp)
- P-only overshoot matches the damping-ratio formula (within 0.5 %)
- at rest, the integral alone holds the spring (I = k·r = 20 N)
- the force never exceeds the 30 N limit
- anti-windup reduces overshoot (12.25 % → 0 %)
- derivative on measurement removes the kick (30 300 N → 300 N)
- the final gains meet all three targets

## Author

Sannidhi D Math