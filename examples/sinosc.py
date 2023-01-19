from pychuck import *
import random

s = SinOsc()
s >> dac

while True:
    s.freq = random.randrange(100, 1000)
    Dur(100, "ms") >> now
