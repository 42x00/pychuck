from pychuck import *

m = Mandolin()
r = JCRev(mix=.025, gain=.75)

m >> r >> dac

notes = [61, 63, 65, 66, 68, 66, 65, 63]

while True:
    m.bodySize = np.random.uniform(0, 1)
    m.pluckPos = np.random.uniform(0, 1)

    factor = np.random.uniform(1, 4)
    for note in notes:
        m.freq = Std.mtof(np.random.randint(0, 3) * 12 + note)
        m.pluck(np.random.uniform(.6, .9))
        now += 100 * ms * factor
