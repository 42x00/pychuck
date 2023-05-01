from pychuck import *

s = Blit(gain=.5)
e = ADSR(A=5 * ms, D=3 * ms, S=.5, R=5 * ms)
r = JCRev(mix=.05)

s >> r >> dac

hi = [0, 2, 4, 7, 9, 11]
while True:
    s.freq = Std.mtof(33 + np.random.randint(0, 3) * 12 + np.random.choice(hi))
    s.harmonics = np.random.randint(1, 5)
    e.keyOn()
    now += 120 * ms
    e.keyOff()
    now += 5 * ms
