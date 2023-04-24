from pychuck import *

i = Impulse()
f = BiQuad(prad=.99, eqzs=True, gain=.5)

i >= f >= dac

v = 0.0
while True:
    i.next = 1
    f.pfreq = np.abs(np.sin(v)) * 800
    v += .1
    now += 101 * ms
