from pychuck import *

adc >> (g := Gain()) >> dac
g >> Gain(gain=.5) >> Delay(delay=.75 * second, gain=.75) >> g

while True:
    now += 1 * second
