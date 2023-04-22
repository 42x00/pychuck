from pychuck import *

(i := Impulse()) >= dac

while True:
    i.next = 1
    now += 200 * ms
