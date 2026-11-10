import numpy as np
from plant import simulate_lag3
from pid import PID


def growth_ratio(kp):
    """Swing size late (50-60 s) divided by swing size early (20-30 s), P only."""
    t, y, u = simulate_lag3(PID(kp, 0, 0), T=60.0)
    centre = y[t > 20].mean()                                   # the level it swings around
    early = np.abs(y[(t > 20) & (t < 30)] - centre).max()
    late = np.abs(y[(t > 50) & (t < 60)] - centre).max()
    return late / early


def measure_tu(kp):
    """Average time between upward crossings of the centre line, P only."""
    t, y, u = simulate_lag3(PID(kp, 0, 0), T=60.0)
    yy = y - y[t > 20].mean()                                  # swing around zero
    up = t[1:][(yy[:-1] < 0) & (yy[1:] >= 0)]                  # times where it crosses upward
    up = up[up > 20]                                           # ignore the start-up part
    return np.diff(up).mean()                                  # average gap = one period


if __name__ == "__main__":
    from metrics import metrics

    Ku = 8.01                                   # from the growth-ratio search (theory: 8)
    Tu = measure_tu(Ku)
    print(f"Ku = {Ku:.2f}, Tu = {Tu:.3f} s   (theory: 8, 2*pi/sqrt(3) = {2*np.pi/np.sqrt(3):.3f} s)")

    Kp = 0.6 * Ku                               # Ziegler-Nichols PID row
    Ti = Tu / 2
    Td = Tu / 8
    Ki = Kp / Ti                                # convert to the form our PID class uses
    Kd = Kp * Td
    print(f"ZN gains: Kp = {Kp:.2f}, Ti = {Ti:.3f} s, Td = {Td:.3f} s  ->  Ki = {Ki:.2f}, Kd = {Kd:.2f}")

    t, y, u = simulate_lag3(PID(Kp, Ki, Kd), T=25.0)
    rise, os_, settle, sse = metrics(t, y)
    print(f"ZN result: rise {rise:.2f} s, overshoot {os_:.1f} %, settle {settle:.1f} s")

    print()
    print("Hand tuning, one change at a time:")
    steps = [("1. ZN table",       (Kp, Ki, Kd)),
             ("2. less I",         (4.81, 1.0, 2.18)),
             ("3. more D",         (4.81, 1.0, 2.75)),
             ("4. less P and I",   (3.6, 0.7, 2.75))]
    for name, gains in steps:
        t, y, u = simulate_lag3(PID(*gains), T=25.0)
        rise, os_, settle, sse = metrics(t, y)
        g = ", ".join(f"{v:.2f}" for v in gains)
        print(f"  {name:16s} ({g}) | rise {rise:.2f} s | overshoot {os_:5.1f} % | settle {settle:4.1f} s")