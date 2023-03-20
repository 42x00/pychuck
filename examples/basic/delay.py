from pychuck import *

delay = Delay(delay=.75 * second)
SinOsc() >> delay >> dac

while True:
    now += 1 * second
