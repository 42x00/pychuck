from pychuck import *

c = SinOsc(freq=440)
m = SinOsc(freq=110, gain=300)

c.sync = 2
