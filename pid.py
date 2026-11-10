import numpy as np


class PID:
    def __init__(self, kp, ki, kd, u_min=-np.inf, u_max=np.inf, anti_windup=False,
                 tau_d=0.0, d_on="error"):          # NEW: d_on = "error" or "measurement"
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.u_min = u_min                  # motor limits (N); ±infinity = no limit
        self.u_max = u_max
        self.anti_windup = anti_windup      # True = clamping anti-windup
        self.tau_d = tau_d                  # D filter time constant (s); 0 = no filter
        self.d_on = d_on                    # NEW: where D gets its rate of change from
        self.integral = 0.0                 # running total of error (m·s)
        self.e_prev = None                  # previous error
        self.y_prev = None                  # NEW: previous measurement
        self.d_filt = 0.0                   # smoothed derivative
        self.history = []                   # (P, I, D) for every step

    def update(self, r, y, dt):
        e = r - y

        # CHANGED: the derivative comes from the measurement or from the error
        if self.d_on == "measurement":
            if self.y_prev is None:
                deriv = 0.0
            else:
                deriv = -(y - self.y_prev) / dt      # minus: y rising = error shrinking
        else:
            if self.e_prev is None:
                deriv = 0.0
            else:
                deriv = (e - self.e_prev) / dt

        alpha = dt / (self.tau_d + dt)                       # 1.0 when tau_d = 0 (no smoothing)
        self.d_filt = self.d_filt + alpha * (deriv - self.d_filt)
        P = self.kp * e
        D = self.kd * self.d_filt
        I_try = self.ki * (self.integral + e * dt)           # I part IF we integrate this step
        u_unsat = P + I_try + D                              # what the controller wants
        u = min(max(u_unsat, self.u_min), self.u_max)        # what the motor can give

        pushing_further_up = u_unsat > self.u_max and e > 0
        pushing_further_down = u_unsat < self.u_min and e < 0
        if not self.anti_windup or not (pushing_further_up or pushing_further_down):
            self.integral = self.integral + e * dt

        I = self.ki * self.integral
        self.history.append((P, I, D))
        self.e_prev = e
        self.y_prev = y                      # NEW: remember the measurement
        return u


if __name__ == "__main__":
    from plant import simulate
    from metrics import metrics
    t, x, u = simulate(pid=PID(300, 400, 30), T=6.0)
    print("D on error:       first three forces:", u[:3])
    print(metrics(t, x))
    t, x, u = simulate(pid=PID(300, 400, 30, d_on="measurement"), T=6.0)   # NEW: second check
    print("D on measurement: first three forces:", u[:3])
    print(metrics(t, x))