import random

from pychuck import *

filename = 'data/snare.wav'

buf = SndBuf(filename=filename)
buf >> dac

while True:
    buf.pos = 0
    buf.gain = random.uniform(.2, .5)
    # buf.rate = random.uniform(.5, 1.5)
    now += 100 * ms
