from pychuck import *

i = Sndbuf('special:glot_pop', rate=1)
f = BiQuad(prad=.8, eqzs=1, gain=.1)
f2 = BiQuad(prad=.995, eqzs=1, gain=.1)
f3 = BiQuad(prad=.995, eqzs=1, gain=.01)
g = Gain()
r = JCRev(mix=.05)

i >> f >> g >> r >> dac
i >> f2 >> g
i >> f3 >> g

v = 0

while True:
    i.pos = 0

    f.pfreq = v2 = 250 + np.sin(v * 100) * 20
    f2.pfreq = 2290 + np.sin(v * 200) * 50
    f3.pfreq = 3010 + np.sin(v * 300) * 80

    v += .05
    g.gain = .2 + np.sin(v) * .1

    now += (1000 + np.random.uniform(-100, 100)) * ms
