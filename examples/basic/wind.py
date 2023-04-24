from pychuck import *

n = Noise()
f = BiQuad(prad=.99, eqzs=True, gain=.05)

n >= f >= dac

t = 0.0
while True:
    f.pfreq = 100 + np.abs(np.sin(t)) * 15000
    t += .01
    now += 5 * ms
