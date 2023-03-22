import random

from pychuck import *

s = SinOsc(gain=.2)
s >> dac
# s >> JCRev(mix=.1) >> dac

hi = [0, 2, 4, 7, 9, 11]
while True:
    s.freq = Std.mtof(45 + random.randint(0, 3) * 12 + random.choice(hi))
    now += 100 * ms
