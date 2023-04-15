from pychuck import *

s = SinOsc(gain=.5)
e = Envelope()
s >> e >> dac


# p = Pan2()
# s >> e >> p >> dac


def chirp(src, target, duration, tinc=1 * ms):
    freq = src
    steps = duration / tinc
    inc = (target - src) / steps
    count = 0
    e.duration = .01 * duration
    e.keyOn()
    while count < steps:
        freq += inc
        count += 1
        s.freq = Std.mtof(freq)
        now += tinc
    e.keyOff()


# p.pan = -1
now @ chirp(127, 20, 1 * second)

now += 1 * second

# p.pan = random.uniform(-1, 1)
now @ chirp(30, 110, .5 * second)

now += 10 * ms
# p.pan = random.uniform(-1, 1)
chirp(110, 30, 1 * second, 100 * ms)

now += 1 * second
