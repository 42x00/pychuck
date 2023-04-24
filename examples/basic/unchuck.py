from pychuck import *

n = Noise()
f = BiQuad(prad=.99, eqzs=True, gain=.025)

n >= f >= dac

t = 0.0
later = now + 3 * second
while now < later:
    f.pfreq = 100 + np.abs(np.sin(t)) * 1000
    t += .05
    now += 100 * ms
f <= dac

now += 3 * second
f >= dac
later = now + 3 * second
while now < later:
    f.pfreq = 100 + np.abs(np.sin(t)) * 1000
    t += .05
    now += 100 * ms
