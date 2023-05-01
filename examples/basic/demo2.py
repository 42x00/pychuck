from pychuck import *

dac.gain = .1

oscarray = [SinOsc(freq=2 ** i * 110) for i in range(5)]

for i in range(5):
    oscarray[i] >> dac

for i in range(5):
    oscarray[i] << dac
    now += 1 * second
