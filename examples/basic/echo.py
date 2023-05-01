from pychuck import *

g = Gain(gain=.75)
feedback = Gain(gain=.5)
delay = DelayL(max=.75 * second, delay=.75 * second)

adc >> g >> dac
g >> feedback >> delay >> g

while True:
    now += 1 * second
