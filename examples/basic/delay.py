from pychuck import *

adc >> Delay(delay=.75 * second) >> dac

while True:
    now += 1 * second
