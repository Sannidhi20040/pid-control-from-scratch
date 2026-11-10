import os
import numpy as np
import matplotlib.pyplot as plt
from plant import simulate,simulate_lag3
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

def fig08_windup():
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.8))     # 1 row, 3 graphs side by side
    for aw, color, name in [(False, "tab:red", "no anti-windup"),
                            (True, "tab:green", "with anti-windup (clamping)")]:
        pid = PID(300, 400, 30, u_min=-30, u_max=30, anti_windup=aw)
        t, x, u = simulate(pid=pid, T=4.0)
        I = np.array(pid.history)[:, 1]
        axs[0].plot(t, x, color=color, label=name)
        axs[1].plot(t, u, color=color, label=name)
        axs[2].plot(t, I, color=color, label=f"{name} (max {I.max():.0f} N)")

    axs[0].axhline(1.0, linestyle="--", color="k", label="target 1 m")
    axs[0].set(title="Position", xlabel="time (s)", ylabel="position (m)")
    axs[1].axhline(30, linestyle=":", color="k", label="motor limit ±30 N")
    axs[1].axhline(-30, linestyle=":", color="k")
    axs[1].set(title="Force sent to motor", xlabel="time (s)", ylabel="force (N)")
    axs[2].axhline(20, linestyle=":", color="gray", label="20 N needed at 1 m")
    axs[2].set(title="I part (the stored-up push)", xlabel="time (s)", ylabel="force (N)")
    for ax in axs:
        ax.legend(fontsize=7)
        ax.grid(True)
    fig.suptitle("Integral windup: motor limited to 30 N, gains (300, 400, 30)")
    fig.tight_layout()
    fig.savefig("figures/fig08_windup.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved fig08")

def fig09_noise():
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8))
    for tau, color, name in [(0.0, "tab:blue", "raw D"),
                             (0.02, "tab:orange", "D filtered (τ = 0.02 s)")]:
        t, x, u = simulate(pid=PID(300, 400, 30, tau_d=tau), T=5.0, noise=0.001)   # CHANGED: 5 s, same as the table
        steady = t > 2
        axs[0].plot(t, u, color=color, linewidth=0.6 if tau == 0 else 1.4,
                    label=f"{name}: force noise {u[steady].std():.1f} N")
    axs[0].set(title="Force with ±1 mm sensor noise", xlabel="time (s)", ylabel="force (N)",
               ylim=(-100, 150))

    # Zoom: rebuild the same noise the controller saw (same seed, same order of draws)
    t, x, u = simulate(pid=PID(300, 400, 30), T=3.0, noise=0.001)
    rng = np.random.default_rng(0)
    noise_vals = np.array([rng.uniform(-0.001, 0.001) for _ in range(len(t))])
    y = x + noise_vals
    zoom = (t > 2.0) & (t < 2.1)
    axs[1].plot(t[zoom], y[zoom] * 1000, color="gray", linewidth=0.8, label="what the sensor reports")
    axs[1].plot(t[zoom], x[zoom] * 1000, color="tab:green", linewidth=2, label="true position")
    axs[1].set(title="Zoom: 0.1 s of sensor readings", xlabel="time (s)", ylabel="position (mm)")

    for ax in axs:
        ax.legend(fontsize=8)
        ax.grid(True)
    fig.tight_layout()
    fig.savefig("figures/fig09_noise.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved fig09")

def fig10_kick():
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8))
    for d, color in [("error", "tab:red"), ("measurement", "tab:green")]:
        t, x, u = simulate(pid=PID(300, 400, 30, d_on=d), T=1.5, r_time=0.5)
        axs[0].plot(t, x, color=color, label=f"D on {d}")
        axs[1].plot(t, u, color=color, label=f"D on {d} (peak {u.max():,.0f} N)")
    r_line = np.where(t >= 0.5, 1.0, 0.0)              # the target: 0, then 1 from t = 0.5 s
    axs[0].plot(t, r_line, "k--", label="target (jumps at 0.5 s)")
    axs[0].set(title="Position", xlabel="time (s)", ylabel="position (m)")
    axs[1].set_yscale("symlog", linthresh=100)        # log-like scale so 300 N and 30,000 N both show
    axs[1].set(title="Force (log-like scale)", xlabel="time (s)", ylabel="force (N)")
    for ax in axs:
        ax.legend(fontsize=8)
        ax.grid(True)
    fig.suptitle("Derivative kick: the target jumps from 0 to 1 m at t = 0.5 s")
    fig.tight_layout()
    fig.savefig("figures/fig10_kick.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved fig10")

def fig11_period():
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8))
    for Ts in [0.001, 0.02, 0.05, 0.07]:
        t, x, u = simulate(pid=PID(300, 400, 30), T=3.0, Ts=Ts)
        axs[0].plot(t, x, label=f"update every {Ts*1000:.0f} ms (peak {x.max():.2f} m)")
    axs[0].axhline(1.0, linestyle="--", color="k", label="target 1 m")
    axs[0].set(title="Same gains, slower and slower controller", xlabel="time (s)",
               ylabel="position (m)", ylim=(-1, 3))

    for Ts, color, name in [(0.001, "tab:green", "every 1 ms"), (0.05, "tab:orange", "every 50 ms")]:
        t, x, u = simulate(pid=PID(300, 400, 30), T=0.5, Ts=Ts)
        axs[1].plot(t, u, color=color, label=f"force updated {name}")
    axs[1].set(title="A slow controller holds each force until the next update",
               xlabel="time (s)", ylabel="force (N)")

    for ax in axs:
        ax.legend(fontsize=8)
        ax.grid(True)
    fig.suptitle("Slow update rate, gains (300, 400, 30), no force limit")
    fig.tight_layout()
    fig.savefig("figures/fig11_period.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved fig11")

def fig12_ku():
    plt.figure(figsize=(7, 4))
    for kp in [4, 6, 8.01, 9]:
        t, y, u = simulate_lag3(PID(kp, 0, 0), T=25.0)
        plt.plot(t, y, linewidth=2.2 if kp == 8.01 else 1.2, label=f"P only, Kp = {kp}")
    plt.ylim(-0.6, 2.4)
    plt.xlabel("time (s)")
    plt.ylabel("output (no units)")
    plt.title("Finding Ku on 1/(s+1)³: raise Kp until the swing neither grows nor dies")
    plt.legend(fontsize=8, loc="lower right")
    plt.grid(True)
    plt.savefig("figures/fig12_ku.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("saved fig12")


def fig13_zn():
    plt.figure(figsize=(7, 4))
    steps = [("1. ZN table", (4.81, 2.65, 2.18)), ("2. less I", (4.81, 1.0, 2.18)),
             ("3. more D", (4.81, 1.0, 2.75)), ("4. less P and I", (3.6, 0.7, 2.75))]
    for name, gains in steps:
        t, y, u = simulate_lag3(PID(*gains), T=25.0)
        rise, os_, settle, sse = metrics(t, y)
        plt.plot(t, y, linewidth=2.2 if name.startswith("4") else 1.3,
                 label=f"{name} {gains}: overshoot {os_:.0f}%, settle {settle:.1f} s")
    plt.axhline(1.0, linestyle="--", color="k", label="target 1")
    plt.xlim(0, 15)
    plt.xlabel("time (s)")
    plt.ylabel("output (no units)")
    plt.title("Ziegler–Nichols, then improving it by hand")
    plt.legend(fontsize=7, loc="lower right")
    plt.grid(True)
    plt.savefig("figures/fig13_zn.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("saved fig13")

if __name__ == "__main__":
    fig01_open_loop()
    fig02_metrics()
    fig03_p_sweep()
    fig04_pi()
    fig05_pd()
    fig06_compare()
    fig07_parts()
    fig08_windup()
    fig09_noise()
    fig10_kick()
    fig11_period()
    fig12_ku()
    fig13_zn()