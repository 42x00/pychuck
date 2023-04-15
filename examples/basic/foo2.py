from pychuck import *

s = Blit(gain=.5, harmonics=4)
p = Pan2()
r1 = JCRev(mix=.1)
r2 = JCRev(mix=.1)

s >> p
p.left >> r1 >> dac.left
p.right >> r2 >> dac.right

hi = [0, 2, 4, 7, 9, 11]


def dopan():
    t = 0
    while True:
        p.pan = .7 * np.sin(t)
        t += .005
        now += 10 * ms


spork(dopan())

while True:
    s.freq = Std.mtof(33 + np.random.randint(0, 3) * 12 + np.random.choice(hi))
    now += 120 * ms
