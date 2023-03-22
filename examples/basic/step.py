from pychuck import *

s = Step()
s >> dac

v = .5
while True:
    now += 1 * ms
    s.next = v
    v = -v
