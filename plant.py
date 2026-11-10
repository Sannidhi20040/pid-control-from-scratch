import numpy as np
import matplotlib.pyplot as plt


def simulate(pid=None, u=20.0, r=1.0, m=1.0, c=10.0, k=20.0, T=4.0, dt=0.001,
             noise=0.0, seed=0, r_time=0.0, Ts=None):     # NEW: Ts = controller update period (s)
    rng = np.random.default_rng(seed)                 # random number generator (repeatable)
    n = int(round(T / dt))
    t = np.arange(1, n + 1) * dt
    xs = np.zeros(n)
    us = np.zeros(n)
    x, v = 0.0, 0.0
    if Ts is None:
        Ts = dt                                       # NEW: default = update every physics step
    every = max(1, int(round(Ts / dt)))               # NEW: run the controller every `every` steps
    for i in range(n):
        y = x + rng.uniform(-noise, noise)            # what the sensor reports
        r_now = r if i * dt >= r_time else 0.0        # target is 0 until r_time, then r
        if pid is not None and i % every == 0:        # CHANGED: only on update steps
            u = pid.update(r_now, y, every * dt)      # CHANGED: the controller's own time step
        a = (u - k * x - c * v) / m                   # physics uses the TRUE x, still every 1 ms
        v = v + a * dt
        x = x + v * dt
        xs[i] = x
        us[i] = u                                     # between updates u is simply held
    return t, xs, us


if __name__ == '__main__':
    t, x, u = simulate()
    t2, x2, u2 = simulate(k=25.0)
    t3, x3, u3 = simulate(k=16.0)
    plt.plot(t, x, label="k = 20 N/m")
    plt.plot(t2, x2, label="k = 25 N/m")
    plt.plot(t3, x3, label="k = 16 N/m")

    plt.axhline(1.0, linestyle="--", color="k", label="target 1 m")
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.title("Open loop, constant 20 N: the result depends on the spring")
    plt.legend()
    plt.grid(True)

    print(f"k=20: final x = {x[-1]:.4f} m")
    print(f"k=25: final x = {x2[-1]:.4f} m")
    print(f"k=16: final x = {x3[-1]:.4f} m")

    plt.show()