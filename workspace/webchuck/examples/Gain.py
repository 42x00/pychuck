from pychuck import *

s = SinOsc()
g = Gain(gain=.5)

s >> g >> dac

while True:
    g.gain = np.random.uniform(0, 1)
    now += 200 * ms
