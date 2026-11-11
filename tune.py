import numpy as np
from plant import simulate
from pid import PID
from metrics import metrics

# My targets (with 30 N limit, anti-windup, filter, ±1 mm noise all ON):
OS_MAX = 2.0        # overshoot, %
SETTLE_MAX = 1.0    # settling time, s
NOISE_MAX = 1.0     # force noise (std over the last second), N

# My final choice: (150, 300, 15)
# Reason: balance between motor longevity (low force noise) and robustness
# (still meets the targets with a 2 kg load; never fails badly).


def test(kp, ki, kd, limit=30, **plant_changes):
    """Run one gain set with every real-world problem switched on."""
    pid = PID(kp, ki, kd, u_min=-limit, u_max=limit, anti_windup=True,
              tau_d=0.02, d_on="measurement")
    t, x, u = simulate(pid=pid, T=5.0, noise=0.001, **plant_changes)
    r = plant_changes.get("r", 1.0)
    rise, os_, settle, sse = metrics(t, x, r=r)
    force_noise = u[t > 4].std()
    return rise, os_, settle, sse, force_noise


if __name__ == "__main__":
    candidates = [(100, 200, 10), (150, 300, 15), (200, 400, 20), (300, 400, 30),
                  (400, 400, 20), (200, 800, 20), (200, 400, 40), (200, 0, 20)]
    print("gains            | rise    | overshoot | settle  | noise  | meets targets?")
    for g in candidates:
        rise, os_, settle, sse, nz = test(*g)
        ok = os_ < OS_MAX and settle < SETTLE_MAX and nz < NOISE_MAX
        print(f"{str(g):16s} | {rise:.3f} s | {os_:6.2f} %  | {settle:.3f} s | {nz:.2f} N | {'YES' if ok else 'no'}")

    print("\nStress test of my choice (150, 300, 15):")
    tests = [("base", 30, {}), ("mass 2 kg", 30, dict(m=2.0)), ("mass 5 kg", 30, dict(m=5.0)),
             ("limit 15 N", 15, {}), ("limit 25 N", 25, {}), ("target 2 m", 30, dict(r=2.0)),
             ("spring 40", 30, dict(k=40.0)), ("damper 2", 30, dict(c=2.0)),
             ("update 100 ms", 30, dict(Ts=0.1))]
    for label, lim, changes in tests:
        rise, os_, settle, sse, nz = test(150, 300, 15, limit=lim, **changes)
        print(f"{label:14s} | rise {rise:.3f} s | os {os_:5.2f} % | settle {settle:.3f} s | noise {nz:.2f} N | error {sse:.3f} m")