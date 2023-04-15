from pychuck import *

s = SinOsc(gain=.15)
s >> dac

t = 0.0
while True:
    s.freq = 30 + (np.sin(t) + 1.0) * 10000.0
    t += .004
    now += 1 * ms
