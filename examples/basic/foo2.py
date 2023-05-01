from pychuck import *

s = Blit(harmonics=4, gain=.5)
p = Pan2()
r1 = JCRev(mix=.1)
r2 = JCRev(mix=.1)

s >> p
p.left >> r1 >> dac.left
p.right >> r2 >> dac.right


def dopan():
    t = 0
    while True:
        p.pan = np.sin(t) * .7
        t += .005
        now += 10 * ms


spork(dopan())

hi = [0, 2, 4, 7, 9, 11]
while True:
    s.freq = Std.mtof(33 + np.random.randint(0, 3) * 12 + np.random.choice(hi))
    now += 120 * ms
