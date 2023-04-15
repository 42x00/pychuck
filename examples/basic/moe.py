from pychuck import *

i = Impulse()
f = BiQuad(prad=.99, eqzs=1, gain=.5)
i >> f >> dac

v = 0
while True:
    i.next = 1
    f.pfreq = np.abs(np.sin(v)) * 4000
    v += .1
    now += 100 * ms
