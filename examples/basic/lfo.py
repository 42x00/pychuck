from pychuck import *

lfo = SinOsc()
lfo >> blackhole

while True:
    print(lfo.last)
    now += 50 * ms
