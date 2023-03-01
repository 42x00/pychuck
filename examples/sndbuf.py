import random

from pychuck import *

buf = SndBuf()
buf >> dac

buf.read('/Users/ykli/research/pychuck/data/snare.wav')

while True:
    buf.pos = 0
    buf.gain = random.uniform(0.2, 0.5)
    buf.rate = random.uniform(0.5, 1.5)
    Dur(100, "ms") >> now
