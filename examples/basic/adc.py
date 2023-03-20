# mic-in to audio out

from pychuck import *

# the patch
adc >> Gain() >> dac

# infinite time-loop
while True:
    # advance time
    Dur(100, ms) >> now
