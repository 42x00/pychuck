from pychuck import *

g = Gain(gain=.5)
g >> dac

freq = 110.0
x = 6

while x > 0:
    s = SinOsc(freq=freq)
    s >> g
    freq *= 2
    x -= 1
    now += 1 * second
    s << g
