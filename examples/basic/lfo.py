from pychuck import *

lfo = SinOsc(freq=1)

lfo >= blackhole

while True:
    print(lfo.last)
    now += 50 * ms
