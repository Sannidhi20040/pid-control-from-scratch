import numpy as np
import matplotlib.pyplot as plt

def simulate(u=20.0, m=1.0, c=10.0, k= 20.0, T=4.0, dt=0.001):
    n = int(round(T/dt))
    t = np.arange(1, n+1)*dt
    xs = np.zeros(n)
    x, v = 0.0, 0.0
    for i in range(n):
        a = (u - k*x - c*v)/m
        v = v + a * dt
        x = x + v * dt
        xs[i] = x
    return t,xs

if __name__ == '__main__':
    t, x = simulate()
    t2, x2 = simulate(k=25.0)
    plt.plot(t,x, label="k = 20 N/m")
    plt.plot(t2,x2, label="k = 25 N/m")
    t3, x3 = simulate(k=16.0)
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