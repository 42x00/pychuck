from pychuck import *

filename = 'foo.wav'

dac >> Gain(gain=.5) >> WvOut(filename=filename) >> blackhole
print(f'writing to file: "{filename}"')

while True:
    now += 1 * second
