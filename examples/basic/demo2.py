from pychuck import *

dac.gain = .1

oscarray = [SinOsc(freq=2 ** i * 110) for i in range(5)]
for osc in oscarray:
    osc >> dac

for osc in oscarray:
    osc << dac
    now += 1 * second
