from pychuck import *
import random

s = SinOsc()
s >> dac

while True:
    s.freq = random.randrange(30, 1000)
    Dur(1, "samp") >> now
