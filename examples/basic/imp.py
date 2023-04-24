from pychuck import *

i = Impulse(gain=.5)

i >= dac

a = 2000
while True:
    i.next = 1
    now += a * samp
    a -= 8
    if a <= 0:
        a = 2000
