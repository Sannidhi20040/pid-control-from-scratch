
import numpy as np

def metrics(t, x, r=1.0, band=0.02):
    xf = x[-1]
    i10 = np.argmax(x>= 0.1 * xf)
    i90 = np.argmax(x>=0.9 * xf)
    rise = t[i90] - t[i10]
    overshoot = max(0.0, ((x.max() - xf)/ xf) * 100)
    outside = np.where(np.abs(x-r)>band*r)[0]
    if len(outside) == 0:
        settle = 0.0
    elif outside[-1] == len(x) - 1:
        settle = np.nan
    else:
        settle = t[outside[-1] + 1]

    sse = r - xf

    return rise, overshoot, settle, sse

if __name__ == "__main__":
    from plant import simulate
    t, x, u = simulate()
    rise, os_, settle, sse = metrics(t,x)
    print(f"rise {rise:.3f} s | overshoot {os_: .2f} % | settle {settle:.3f} s | error {sse:.5f} m")