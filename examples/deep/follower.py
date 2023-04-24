from pychuck import *

g = Gain(op=3)
p = OnePole(pole=.99)

adc >= g >= p >= dac
adc >= g

while True:
    if p.last > .01:
        print('BANG!!')
        now += 80 * ms
    now += 20 * ms
