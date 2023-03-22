from pychuck import *

m = SinOsc(freq=110, gain=300)
c = SinOsc()
step = Step()

m >> c >> dac
step >> c

step.next = 440
while True:
    now += 1 * second
