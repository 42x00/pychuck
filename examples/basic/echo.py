from pychuck import *

g = Gain()

adc >> g >> dac
g >> Gain(gain=.5) >> DelayL(max=.75 * second, delay=.75 * second, gain=.75) >> g

while True:
    now += 1 * second
