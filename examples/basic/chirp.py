from pychuck import *

s = SinOsc(gain=.4)

s >> dac


def chirp(src, target, duration, tinc=1 * ms):
    freq = src
    steps = duration / tinc
    inc = (target - src) / steps
    count = 0
    while count < steps:
        freq += inc
        count += 1
        s.freq = Std.mtof(freq)
        now += tinc


now @ chirp(127, 20, 1 * second)

now @ chirp(20, 120, 1.5 * second, 100 * ms)
