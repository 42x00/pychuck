from pychuck import *

s1 = SinOsc(440)
s2 = SinOsc(441)
r = Rave()

s1 >> r
s2 >> r
r >> dac

r.load("/Users/ykli/research/pychuck/checkpoints/percussion.ts")

Dur(1, "m") >> now
