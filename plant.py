m, c, k = 1.0, 10.0, 20.0
u = 20.0
dt = 0.001
n_steps = 4000

x, v = 0.0, 0.0
for i in range(n_steps):
    a = (u - c*v - k*x)/m
    v = v + a*dt 
    x = x + v*dt 
print(f"after {n_steps*dt:.1f} s: x = {x:.4f} m, v = {v:.4f} m/s")