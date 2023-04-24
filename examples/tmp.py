from pychuck import *

i = Impulse()
r = JCRev(mix=0.5)
i >= r >= dac

while True:
    i.next = 1
    now += 200 * ms
