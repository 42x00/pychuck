from pychuck import *

g = Gain()
adc >> g >> dac
SinOsc(freq=400.0) >> g

g.op = 3

while True:
    now += 1 * second
