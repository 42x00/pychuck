from pychuck import *

s = SinOsc(gain=.2)
r = JCRev(mix=.1)

s >> r >> dac

hi = [0, 2, 4, 7, 9, 11]
while True:
    s.freq = Std.mtof(45 + np.random.randint(0, 3) * 12 + np.random.choice(hi))
    now += 100 * ms
