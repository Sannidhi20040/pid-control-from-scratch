import os
import numpy as np
import matplotlib.pyplot as plt
from plant import simulate
from pid import PID
from metrics import metrics

os.makedirs("figures", exist_ok=True)      # create the folder if it doesn't exist yet


def fig01_open_loop():
    plt.figure(figsize=(7, 4))             # new blank figure, 7 x 4 inches
    for k in [16.0, 20.0, 25.0]:
        t, x, u = simulate(k=k, T=6.0)     # 6 s so k = 16 truly settles
        plt.plot(t, x, label=f"k = {k:.0f} N/m (stops at {x[-1]:.2f} m)")
    plt.axhline(1.0, linestyle="--", color="k", label="target 1 m")
    plt.xlim(0, 4)                         # show only the first 4 s
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.title("Open loop: a fixed 20 N push only works if the spring is exactly 20 N/m")
    plt.legend()
    plt.grid(True)
    plt.savefig("figures/fig01_open_loop.png", dpi=150, bbox_inches="tight")
    plt.close()                            # free memory, start fresh for the next figure
    print("saved fig01")


def fig02_metrics():
    t, x, u = simulate(pid=PID(300, 400, 30), T=6.0)     # CHANGED: 6 s so the final value is truly final
    rise, os_, settle, sse = metrics(t, x)
    xf = x[-1]
    i10 = np.argmax(x >= 0.1 * xf)          # same indexes metrics() uses internally
    i90 = np.argmax(x >= 0.9 * xf)
    ipk = np.argmax(x)                      # index of the peak

    plt.figure(figsize=(7, 4))
    plt.axhspan(0.98, 1.02, color="green", alpha=0.15, label="±2% band (0.98–1.02 m)")
    plt.plot(t, x, label="position, PID (300, 400, 30)", linewidth=2)
    plt.axhline(1.0, linestyle="--", color="k", label="target 1 m")

    plt.plot([t[i10], t[i90]], [x[i10], x[i90]], "o", color="red")
    plt.annotate(f"rise time {rise:.2f} s\n(10% → 90%)", xy=(t[i90], x[i90]),
                 xytext=(0.55, 0.45), arrowprops=dict(arrowstyle="->"))
    plt.annotate(f"overshoot {os_:.1f}%\n(peak {x[ipk]:.3f} m)", xy=(t[ipk], x[ipk]),
                 xytext=(0.75, 1.22), arrowprops=dict(arrowstyle="->"))   # CHANGED: two lines, clear of the purple line
    plt.axvline(settle, linestyle=":", color="purple")
    plt.text(settle + 0.03, 0.6, f"settling time {settle:.2f} s\n(stays in band after this)",
             color="purple")
    plt.text(2.1, 0.85, f"steady-state error ≈ 0\n(final {xf:.3f} m)")

    plt.xlim(0, 3)                          # CHANGED: show 0–3 s even though we simulated 6 s
    plt.ylim(0, 1.4)
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.title("The four measures on one step response")
    plt.legend(loc="lower right", fontsize=8)
    plt.grid(True)
    plt.savefig("figures/fig02_metrics.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"saved fig02 | rise {rise:.3f} s, overshoot {os_:.1f} %, settle {settle:.2f} s")   # CHANGED: print the numbers


def fig03_p_sweep():
    plt.figure(figsize=(7, 4))
    for kp in [10, 50, 100, 200, 500]:
        t, x, u = simulate(pid=PID(kp, 0, 0), T=3.0)
        plt.plot(t, x, label=f"Kp = {kp} (stops at {x[-1]:.3f} m)")
    plt.axhline(1.0, linestyle="--", color="k", label="target 1 m")
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.title("P only: higher Kp gets closer and faster, but never reaches 1 m")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.savefig("figures/fig03_p_sweep.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("saved fig03")


def fig04_pi():
    plt.figure(figsize=(7, 4))
    for ki in [0, 100, 400, 1200]:
        t, x, u = simulate(pid=PID(300, ki, 0), T=8.0)       # 8 s so the values have (nearly) settled
        plt.plot(t, x, label=f"Ki = {ki} (x at 8 s = {x[-1]:.3f} m)")   # CHANGED: honest label (Ki = 100 is still creeping)
    plt.axhline(1.0, linestyle="--", color="k", label="target 1 m")
    plt.xlim(0, 3)                                            # show only 0–3 s
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.title("Adding I (Kp = 300): the gap closes, but bouncing grows")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.savefig("figures/fig04_pi.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("saved fig04")


def fig05_pd():
    plt.figure(figsize=(7, 4))
    for kd in [0, 10, 30, 60]:
        t, x, u = simulate(pid=PID(300, 0, kd), T=3.0)
        zeta = (10 + kd) / (2 * np.sqrt(320))       # D adds Kd to the damper; P makes the spring 20 + 300
        plt.plot(t, x, label=f"Kd = {kd} (ζ = {zeta:.2f})")
    plt.axhline(1.0, linestyle="--", color="k", label="target 1 m")
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.title("Adding D (Kp = 300): bouncing dies, the gap stays")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.savefig("figures/fig05_pd.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("saved fig05")


def fig06_compare():
    plt.figure(figsize=(7, 4))
    for name, gains in [("P", (300, 0, 0)), ("PI", (300, 400, 0)),
                        ("PD", (300, 0, 30)), ("PID", (300, 400, 30))]:
        t, x, u = simulate(pid=PID(*gains), T=3.0)
        plt.plot(t, x, label=f"{name} {gains}", linewidth=2.2 if name == "PID" else 1.4)
    plt.axhline(1.0, linestyle="--", color="k", label="target 1 m")
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.title("P, PI, PD and PID compared (Kp = 300)")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.savefig("figures/fig06_compare.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("saved fig06")


def fig07_parts():
    pid = PID(300, 400, 30)                      # keep a handle on the controller...
    t, x, u = simulate(pid=pid, T=3.0)           # ...so we can read its history after the run
    parts = np.array(pid.history)                # 3000 rows x 3 columns: P, I, D
    P, I, D = parts[:, 0], parts[:, 1], parts[:, 2]

    plt.figure(figsize=(7, 4))
    plt.plot(t, P, label="P = Kp·e (present error)")
    plt.plot(t, I, label="I = Ki·∫e dt (accumulated past)", linewidth=2.2)
    plt.plot(t, D, label="D = Kd·de/dt (braking)")
    plt.plot(t, u, label="total force u", color="k", linewidth=1.2)
    plt.axhline(20, linestyle=":", color="gray", label="20 N = spring force at 1 m")
    plt.axhline(0, color="k", linewidth=0.5)
    plt.ylim(-260, 320)
    plt.xlabel("time (s)")
    plt.ylabel("force (N)")
    plt.title("Inside PID (300, 400, 30): what each part is doing")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.savefig("figures/fig07_parts.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"saved fig07 | at t = 3 s: P = {P[-1]:.2f}, I = {I[-1]:.2f}, D = {D[-1]:.2f} N")


if __name__ == "__main__":
    fig01_open_loop()
    fig02_metrics()
    fig03_p_sweep()
    fig04_pi()
    fig05_pd()
    fig06_compare()
    fig07_parts()