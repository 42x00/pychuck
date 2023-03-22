from pychuck import *

s = SinOsc()
s >> dac
# s >> JCRev(gain=.5, mix=.075) >> dac

note = 20

while note < 128:
    s.freq = Std.mtof(note)
    s.gain = .5 - (note / 256.0)
    note += 2
    now += .125 * second

s.gain = 0
now += 2 * second
