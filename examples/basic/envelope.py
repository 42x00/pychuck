import random

from pychuck import *

Noise() >> (e := Envelope()) >> dac

while True:
    e.duration = t = random.uniform(10, 500) * ms
    print(f"rise/fall: {t / ms} ms")
    e.keyOn()
    now += 800 * ms
    e.keyOff()
    now += 800 * ms