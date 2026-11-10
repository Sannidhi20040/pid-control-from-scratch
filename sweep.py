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