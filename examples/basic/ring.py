from pychuck import *

g = Gain(op=3)
s = SinOsc(freq=400.0)

adc >> g >> dac
s >> g

while True:
    now += 1 * second
