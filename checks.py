"""Automatic checks: does my simulation agree with the theory?
Run:  python checks.py     (every line should say PASS)
"""
import numpy as np
from plant import simulate
from pid import PID
from metrics import metrics
from tune import test, OS_MAX, SETTLE_MAX, NOISE_MAX

m, c, k = 1.0, 10.0, 20.0
failures = 0


def check(name, value, expected, tol):
    """PASS if value is within tol of expected."""
    global failures
    ok = abs(value - expected) <= tol
    if not ok:
        failures += 1
    print(f"{'PASS' if ok else 'FAIL'} | {name:42s} | got {value:10.4f} | expected {expected:10.4f} ± {tol}")


# 1. Open loop: force balance says x = u / k
t, x, u = simulate(u=20.0, T=6.0)
check("open loop final position = 20/20", x[-1], 20.0 / k, 0.001)

# 2. P-only final position = Kp / (k + Kp)
for kp in [20, 80, 180]:
    t, x, u = simulate(pid=PID(kp, 0, 0), T=6.0)
    check(f"P-only Kp={kp} final = Kp/(k+Kp)", x[-1], kp / (k + kp), 0.001)

# 3. P-only overshoot matches the zeta formula
kp = 180
zeta = c / (2 * np.sqrt(m * (k + kp)))
os_theory = 100 * np.exp(-np.pi * zeta / np.sqrt(1 - zeta**2))
t, x, u = simulate(pid=PID(kp, 0, 0), T=6.0)
rise, os_, settle, sse = metrics(t, x)
check(f"P-only Kp={kp} overshoot vs formula (%)", os_, os_theory, 0.5)

# 4. Adding I removes the steady-state error
t, x, u = simulate(pid=PID(80, 100, 0), T=10.0)
check("PI final error = 0", 1.0 - x[-1], 0.0, 0.001)

# 5. At rest the integral alone holds the spring: I = k * r
pid = PID(80, 100, 0)
simulate(pid=pid, T=10.0)
P, I, D = pid.history[-1]
check("PI at rest: I term = k*r = 20 N", I, k * 1.0, 0.05)

# 6. The motor limit is never exceeded
pid = PID(300, 300, 30, u_min=-30, u_max=30, anti_windup=True)
t, x, u = simulate(pid=pid, T=5.0)
check("force never above 30 N", np.abs(u).max(), 30.0, 1e-9)

# 7. Anti-windup reduces overshoot
def overshoot(aw):
    pid = PID(80, 100, 0, u_min=-30, u_max=30, anti_windup=aw)
    t, x, u = simulate(pid=pid, T=10.0)
    return metrics(t, x)[1]
os_off, os_on = overshoot(False), overshoot(True)
ok = os_on < os_off
failures += not ok
print(f"{'PASS' if ok else 'FAIL'} | {'anti-windup lowers overshoot':42s} | off {os_off:.2f} %  ->  on {os_on:.2f} %")

# 8. D on measurement removes the derivative kick
#    (target jumps 0 -> 1 at t = 0.5 s, so the controller sees the jump)
def biggest_force(d_on):
    pid = PID(300, 0, 30, d_on=d_on)
    t, x, u = simulate(pid=pid, T=1.0, r_time=0.5)
    return np.abs(u).max()
kick_err, kick_meas = biggest_force("error"), biggest_force("measurement")
ok = kick_meas < kick_err / 10
failures += not ok
print(f"{'PASS' if ok else 'FAIL'} | {'D on measurement removes the kick':42s} | error {kick_err:.0f} N  ->  measurement {kick_meas:.0f} N")

# 9. My final gains still meet my targets
rise, os_, settle, sse, nz = test(150, 300, 15)
ok = os_ < OS_MAX and settle < SETTLE_MAX and nz < NOISE_MAX
failures += not ok
print(f"{'PASS' if ok else 'FAIL'} | {'final gains (150, 300, 15) meet targets':42s} | os {os_:.2f} %, settle {settle:.3f} s, noise {nz:.2f} N")

print("\nALL CHECKS PASSED" if failures == 0 else f"\n{failures} CHECK(S) FAILED")
raise SystemExit(failures)
