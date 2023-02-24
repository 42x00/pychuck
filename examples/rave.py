from pychuck import *

s = SinOsc(440)
r = Rave()

s >> r >> dac

r.load("/Users/ykli/research/pychuck/checkpoints/percussion.ts")

Dur(1, "m") >> now
