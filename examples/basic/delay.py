from pychuck import *

adc >> DelayL(max=.75 * second, delay=.75 * second) >> dac

while True:
    now += 1 * second
