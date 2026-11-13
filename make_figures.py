import os
import numpy as np
import matplotlib.pyplot as plt
from plant import simulate, simulate_lag3
from pid import PID
from metrics import metrics
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

os.makedirs("figures", exist_ok=True)      # create the folder if it doesn't exist yet

def fig00():
    """The feedback loop diagram for Section 1."""
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")

    def box(x, y, w, h, text, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                    fc=color, ec="black", lw=1.5))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=11)

    def arrow(p, q, label=None):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16,
                                     lw=1.5, color="black"))
        if label:
            ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 0.18, label,
                    ha="center", va="bottom", fontsize=9.5)

    # comparison point: error = target - measured
    ax.add_patch(plt.Circle((2.0, 2.8), 0.25, fc="white", ec="black", lw=1.5))
    ax.text(2.0, 2.8, "Σ", ha="center", va="center", fontsize=12)
    ax.text(1.62, 3.08, "+", fontsize=11)
    ax.text(2.08, 2.33, "−", fontsize=13)

    box(3.3, 2.35, 2.0, 0.9, "Controller\n(PID)", "#dbe9f7")
    box(6.6, 2.35, 2.2, 0.9, "Plant\n(mass–spring–damper)", "#fde2c8")
    box(4.6, 0.45, 2.0, 0.8, "Sensor", "#dff2dc")

    arrow((0.2, 2.8), (1.75, 2.8), "target r\n(1 m)")
    arrow((2.25, 2.8), (3.3, 2.8), "error e\n= r − y")
    arrow((5.4, 2.8), (6.6, 2.8), "force u\n(N)")
    arrow((8.9, 2.8), (9.9, 2.8), "position x\n(m)")

    # feedback path: plant -> sensor -> back to the comparison point
    ax.plot([9.4, 9.4], [2.8, 0.85], color="black", lw=1.5)
    arrow((9.4, 0.85), (6.6, 0.85))
    ax.plot([4.6, 2.0], [0.85, 0.85], color="black", lw=1.5)
    arrow((2.0, 0.85), (2.0, 2.55))
    ax.text(3.3, 0.95, "measured y (m)", ha="center", va="bottom", fontsize=9.5)

    ax.set_title("The feedback loop: measure, compare, correct, repeat", fontsize=12)
    fig.tight_layout()
    fig.savefig("figures/fig00_loop.png", dpi=200)
    plt.close(fig)

def fig00b():
    """The test system: forces on the block, for Section 3."""
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.set_xlim(-0.6, 10.2); ax.set_ylim(-1.15, 3.7); ax.axis("off")

    # wall with hatching
    ax.add_patch(Rectangle((-0.35, 0.0), 0.35, 2.6, fc="#dddddd", ec="black", hatch="///", lw=1.2))
    # ground
    ax.plot([0, 9.8], [0, 0], color="black", lw=1.2)
    for gx in np.arange(0.2, 9.8, 0.4):
        ax.plot([gx, gx - 0.2], [0, -0.15], color="gray", lw=0.8)

    bx0, bw, bh = 4.6, 1.6, 1.6   # block

    # spring (top), zig-zag from wall to block
    y_s = 1.95
    xs = np.linspace(0.0, bx0, 200)
    ph = (xs - 0.6) / (bx0 - 1.2) * 9
    tri = 0.22 * (2 * np.abs(2 * (ph - np.floor(ph + 0.5))) - 1)
    zig = np.where((xs > 0.6) & (xs < bx0 - 0.6), tri, 0)
    ax.plot(xs, y_s + zig, color="black", lw=1.6)
    ax.text(bx0 / 2, y_s - 0.55, "spring  k = 20 N/m", ha="center", fontsize=10)

    # damper (bottom): rod + cylinder + piston
    y_d = 0.75
    ax.plot([0, 1.6], [y_d, y_d], color="black", lw=1.6)
    ax.plot([1.6, 2.9], [y_d + 0.28, y_d + 0.28], color="black", lw=1.6)
    ax.plot([1.6, 2.9], [y_d - 0.28, y_d - 0.28], color="black", lw=1.6)
    ax.plot([1.6, 1.6], [y_d - 0.28, y_d + 0.28], color="black", lw=1.6)
    ax.plot([2.4, 2.4], [y_d - 0.2, y_d + 0.2], color="black", lw=2.2)
    ax.plot([2.4, bx0], [y_d, y_d], color="black", lw=1.6)
    ax.text(2.25, y_d - 0.62, "damper  c = 10 N·s/m", ha="center", fontsize=10)

    # block
    ax.add_patch(Rectangle((bx0, 0.05), bw, bh * 1.55, fc="#fde2c8", ec="black", lw=1.6))
    ax.text(bx0 + bw / 2, 1.3, "block\nm = 1 kg", ha="center", va="center", fontsize=11)

    def arrow(x0, x1, y, color, label, ha):
        ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>", mutation_scale=18,
                                     lw=2.2, color=color))
        ax.text(x1 + (0.1 if ha == "left" else -0.1), y, label, ha=ha, va="center",
                fontsize=10.5, color=color)

    # motor push to the right
    ax.add_patch(FancyArrowPatch((bx0 + bw, 1.3), (bx0 + bw + 1.6, 1.3), arrowstyle="-|>",
                                 mutation_scale=18, lw=2.2, color="tab:blue"))
    ax.text(bx0 + bw + 0.8, 1.55, "motor push  u", ha="center", fontsize=10.5, color="tab:blue")
    # resisting forces to the left (drawn above the block)
    arrow(bx0 + 1.2, bx0 - 0.6, 3.45, "tab:red", "spring pulls back  k·x", "right")
    arrow(bx0 + 1.2, bx0 - 0.6, 3.0, "tab:orange", "damper resists motion  c·ẋ", "right")

    # position axis
    ya = -0.55
    ax.add_patch(FancyArrowPatch((bx0, ya), (9.9, ya), arrowstyle="-|>", mutation_scale=14, lw=1.2))
    ax.plot([bx0, bx0], [ya - 0.1, ya + 0.1], color="black")
    ax.text(bx0, ya - 0.33, "x = 0 (start)", ha="center", fontsize=9.5)
    xt = 9.0
    ax.plot([xt, xt], [ya - 0.1, 2.4], color="green", ls="--", lw=1.3)
    ax.text(xt, ya - 0.33, "x = 1 m (target)", ha="center", fontsize=9.5, color="green")
    ax.text(9.95, ya + 0.15, "x", fontsize=11, ha="right")

    ax.set_title("The test system: forces on the block   (m·ẍ = u − k·x − c·ẋ)", fontsize=12, pad=2)
    fig.tight_layout()
    fig.savefig("figures/fig00b_block.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("saved fig00b")


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
    t, x, u = simulate(pid=PID(300, 400, 30), T=6.0)     # 6 s so the final value is truly final
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
                 xytext=(0.75, 1.22), arrowprops=dict(arrowstyle="->"))
    plt.axvline(settle, linestyle=":", color="purple")
    plt.text(settle + 0.03, 0.6, f"settling time {settle:.2f} s\n(stays in band after this)",
             color="purple")
    plt.text(2.1, 0.85, f"steady-state error ≈ 0\n(final {xf:.3f} m)")

    plt.xlim(0, 3)                          # show 0–3 s even though we simulated 6 s
    plt.ylim(0, 1.4)
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.title("The four measures on one step response")
    plt.legend(loc="lower right", fontsize=8)
    plt.grid(True)
    plt.savefig("figures/fig02_metrics.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"saved fig02 | rise {rise:.3f} s, overshoot {os_:.1f} %, settle {settle:.2f} s")


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
        plt.plot(t, x, label=f"Ki = {ki} (x at 8 s = {x[-1]:.3f} m)")
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
        t, x, u = simulate(pid=PID(300, 400, 30, tau_d=tau), T=5.0, noise=0.001)   # 5 s, same as the table
        steady = t > 2
        axs[0].plot(t, u, color=color, linewidth=0.6 if tau == 0 else 1.4,
                    label=f"{name}: force noise {u[steady].std():.1f} N")
    axs[0].set(title="Force with ±1 mm sensor noise", xlabel="time (s)", ylabel="force (N)",
               ylim=(-100, 150), xlim=(0, 3))                          # show 0–3 s of the 5 s run

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
    axs[0].legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)   # legend below the graph

    for Ts, color, name in [(0.001, "tab:green", "every 1 ms"), (0.05, "tab:orange", "every 50 ms")]:
        t, x, u = simulate(pid=PID(300, 400, 30), T=0.5, Ts=Ts)
        axs[1].plot(t, u, color=color, label=f"force updated {name}")
    axs[1].set(title="A slow controller holds each force until the next update",
               xlabel="time (s)", ylabel="force (N)")
    axs[1].legend(fontsize=8)

    for ax in axs:
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
                 label=f"{name} {gains}: overshoot {os_:.1f}%, settle {settle:.1f} s")
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

def fig14():
    """Final design: (150, 300, 15) with every real-world problem switched on."""
    pid = PID(150, 300, 15, u_min=-30, u_max=30, anti_windup=True,
              tau_d=0.02, d_on="measurement")
    t, x, u = simulate(pid=pid, T=5.0, noise=0.001)
    rise, os_, settle, sse = metrics(t, x)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    fig.suptitle("Final design: Kp=150, Ki=300, Kd=15 (30 N limit, ±1 mm noise)")

    ax1.plot(t, x, lw=2, label=f"position: rise {rise:.2f} s, overshoot {os_:.2f} %, settle {settle:.2f} s")
    ax1.axhline(1.0, color="k", ls="--", label="target 1 m")
    ax1.axhspan(0.98, 1.02, color="green", alpha=0.15, label="±2 % band")
    ax1.axvline(settle, color="gray", ls=":", label=f"settled at {settle:.2f} s")
    ax1.set_ylabel("position (m)")
    ax1.legend(loc="lower right"); ax1.grid(True)

    ax2.plot(t, u, lw=1, color="tab:red", label=f"motor force (noise {u[t > 4].std():.2f} N after settling)")
    ax2.axhline(30, color="k", ls=":", label="30 N motor limit")
    ax2.axhline(20, color="tab:green", ls="--", label="20 N = force to hold the spring at 1 m")
    ax2.set_xlabel("time (s)"); ax2.set_ylabel("force (N)")
    ax2.set_ylim(0, 35)
    ax2.set_xlim(0, 3)       # simulate 5 s
    ax2.set_xlim(0, 3)       # simulate 5 s (to measure noise), show the first 3 s
    ax2.legend(loc="lower right"); ax2.grid(True)

    fig.tight_layout()
    fig.savefig("figures/fig14_final.png", dpi=150)
    plt.close(fig)
    print("saved fig14")


if __name__ == "__main__":
    fig00()
    fig00b()
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
    fig14()