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
        t, x, u = simulate(k=k, T=6.0)     # CHANGED: 6 s so k = 16 truly settles
        plt.plot(t, x, label=f"k = {k:.0f} N/m (stops at {x[-1]:.2f} m)")
    plt.axhline(1.0, linestyle="--", color="k", label="target 1 m")
    plt.xlim(0, 4)                         # CHANGED: still show only the first 4 s
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.title("Open loop: a fixed 20 N push only works if the spring is exactly 20 N/m")
    plt.legend()
    plt.grid(True)
    plt.savefig("figures/fig01_open_loop.png", dpi=150, bbox_inches="tight")
    plt.close()                            # free memory, start fresh for the next figure
    print("saved fig01")


# CHANGED: the extra `if __name__ == "__main__":` block that was here is removed


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
        t, x, u = simulate(pid=PID(300, ki, 0), T=8.0)   # CHANGED: 8 s so "final" is really final
        plt.plot(t, x, label=f"Ki = {ki} (final {x[-1]:.3f} m)")
    plt.axhline(1.0, linestyle="--", color="k", label="target 1 m")
    plt.xlim(0, 3)                                          # CHANGED: still show only 0–3 s
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


if __name__ == "__main__":
    fig01_open_loop()
    fig03_p_sweep()
    fig04_pi()
    fig05_pd()
    fig06_compare()