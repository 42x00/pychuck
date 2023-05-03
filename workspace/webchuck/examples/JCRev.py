from pychuck import *

s = SinOsc(freq=800)
r = JCRev(mix=.025)

s >> r >> dac

while True:
    s.gain = 1
    now += 300 * ms
    s.gain = 0
    now += 300 * ms
