class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.e_prev = None

    def update (self, r, y, dt):
        e = r -y
        self.integral = self.integral + e*dt
        if self.e_prev is None:
            deriv = 0.0
        else:
            deriv = (e- self.e_prev)/dt
        u = self.kp*e + self.ki*self.integral + self.kd*deriv
        self.e_prev = e
        return u 

if __name__ == "__main__":
    from plant import simulate
    from metrics import metrics
    t, x, u = simulate(pid = PID(300, 400, 30),T= 6.0)
    print("first three forces:", u[:3])
    print(metrics(t,x))