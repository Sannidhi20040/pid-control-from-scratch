import numpy as np


class PID:
    def __init__(self, kp, ki, kd, u_min=-np.inf, u_max=np.inf, anti_windup=False):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.u_min = u_min                  # NEW: motor limits (N); ±infinity = no limit
        self.u_max = u_max
        self.anti_windup = anti_windup      # NEW: True = use clamping
        self.integral = 0.0
        self.e_prev = None
        self.history = []

    def update(self, r, y, dt):
        e = r - y
        if self.e_prev is None:
            deriv = 0.0
        else:
            deriv = (e - self.e_prev) / dt
        P = self.kp * e
        D = self.kd * deriv
        I_try = self.ki * (self.integral + e * dt)        # NEW: the I part IF we integrate this step
        u_unsat = P + I_try + D                           # what the controller WANTS
        u = min(max(u_unsat, self.u_min), self.u_max)     # NEW: what the motor can GIVE (clip)

        # NEW: decide whether to add this step's error to the running total
        pushing_further_up = u_unsat > self.u_max and e > 0
        pushing_further_down = u_unsat < self.u_min and e < 0
        if not self.anti_windup or not (pushing_further_up or pushing_further_down):
            self.integral = self.integral + e * dt

        I = self.ki * self.integral
        self.history.append((P, I, D))
        self.e_prev = e
        return u


if __name__ == "__main__":
    from plant import simulate
    from metrics import metrics
    t, x, u = simulate(pid=PID(300, 400, 30), T=6.0)
    print("first three forces:", u[:3])
    print(metrics(t, x))