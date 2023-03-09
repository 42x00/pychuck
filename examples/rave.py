from pychuck import *
from pychuck.module.torch import Rave

s = SinOsc(440)
r = Rave()

s >> r >> dac

r.load("/Users/ykli/research/pychuck/checkpoints/rave_chafe_data_rt.ts")

Dur(1, "day") >> now
