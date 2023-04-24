from pychuck import *

n = Noise()
f = BiQuad(prad=.99, eqzs=True, gain=.05)

n >= f >= dac


def wind_gain():
    g = 0
    while True:
        n.gain = np.abs(np.sin(g))
        g += .001
        now += 10 * ms


spork(wind_gain())

t = 0.0
while True:
    f.pfreq = 100 + np.abs(np.sin(t)) * 15000
    t += .01
    now += 5 * ms
