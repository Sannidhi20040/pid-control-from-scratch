
import matplotlib.pyplot as plt

m, c, k = 1.0, 10.0, 20.0
u = 20.0
dt = 0.001
n_steps = 4000
ts, xs = [], []
x, v = 0.0, 0.0
for i in range(n_steps):
    a = (u - c*v - k*x)/m
    v = v + a*dt 
    x = x + v*dt 
    ts.append((i*1) * dt)
    xs.append(x)
print(f"after {n_steps*dt:.1f} s: x = {x:.4f} m, v = {v:.4f} m/s")

plt.plot(ts, xs, label="position x (u = 20 N constant)")
plt.axhline(1.0, linestyle="--", color="k", label="target 1 m")
plt.xlabel("time (s)")
plt.ylabel("position (m)")
plt.title("Open loop: constant 20 N push")
plt.legend()
plt.grid(True)
plt.show()