from pychuck import *

g = Gain()

adc >> g >> dac
g >> Gain(gain=.5) >> Delay(delay=.75 * second, gain=.75) >> g

while True:
    now += 1 * second
