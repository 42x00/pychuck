import random
from pychuck import *


def main():
    s = SinOsc()
    s >> dac
    while True:
        s.freq = random.uniform(30, 1000)
        yield Dur(1, "samp")
