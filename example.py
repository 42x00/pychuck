import random
from pychuck import *

s = SinOsc()
s >> dac

while True:
    s.freq = random.randrange(100, 1000)
    Dur(0.1, "s") >> now
