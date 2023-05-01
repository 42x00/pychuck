from pychuck import *

c = SinOsc()
m = SinOsc()

c >> dac
m >> blackhole

cf = 220
m.freq = mf = 550
index = 200
while True:
    c.freq = cf + (index * m.last)
    now += 1 * samp
