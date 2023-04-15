from pychuck import *

lfo = SinOsc()
lfo >> blackhole
lfo.freq = 1

while True:
    print(lfo.last)
    now += 50 * ms
