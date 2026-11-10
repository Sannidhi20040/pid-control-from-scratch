import numpy as np
from plant import simulate
from pid import PID
from metrics import metrics

print("Kp | final sim | final formula | overshoot sim | overshoot formula | rise")

for kp in [10, 50, 100, 200, 500]:
    t, x, u = simulate(pid=PID(kp, 0, 0), T= 6.0)
    rise, os_, settle, sse = metrics(t,x)
    final_pred = kp/(20 + kp)
    zeta = 10/(2*np.sqrt(20 + kp))
    os_pred = np.exp(-np.pi * zeta/np.sqrt(1- zeta**2)) * 100

    x_final = x[-1]
    print(f"{kp:4d} | {x_final:.3f} | {final_pred:.3f} | {os_:5.1f} % | {os_pred:5.1f} % | {rise:.3f} s")

print()
print("controller | rise | overshoot | settle | error")

for name, gains in [("P", (300, 0, 0)), ("PI", (300, 400, 0)), ("PD", (300, 0, 30)), ("PID", (300, 400, 30))]:
    t, x, u = simulate(pid=PID(*gains), T=6.0)
    rise, os_, settle, sse= metrics(t,x)
    print(f"{name:4s} | {rise:.3f} s | {os_:5.1f} % | {settle:.3f} s | {sse:.4f} m")

print()
print("30 N limit | rise | overshoot | settle | max I part")
for aw in [False, True]:
    pid = PID(300, 400, 30, u_min=-30, u_max=30, anti_windup=aw)
    t, x, u = simulate(pid=pid, T=6.0)
    rise, os_, settle, sse = metrics(t, x)
    I_max = np.array(pid.history)[:, 1].max()
    print(f"anti-windup {str(aw):5s} | {rise:.3f} s | {os_:5.1f} % | {settle:.2f} s | {I_max:.1f} N")

print()
print("±1 mm noise | force noise (std) | overshoot")
for tau in [0.0, 0.02, 0.05]:
    t, x, u = simulate(pid=PID(300, 400, 30, tau_d=tau), T=5.0, noise=0.001)
    rise, os_, settle, sse = metrics(t, x)
    steady = t > 2                                   # only look after the block has settled
    print(f"tau_d = {tau:.2f} s | {u[steady].std():6.2f} N | {os_:4.1f} %")

print()
print("target jumps 0 -> 1 m at t = 0.5 s | peak force")
for d in ["error", "measurement"]:
    t, x, u = simulate(pid=PID(300, 400, 30, d_on=d), T=2.0, r_time=0.5)
    print(f"D on {d:11s} | {u.max():9.1f} N")