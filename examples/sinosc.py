from pychuck import *

# patch
s = SinOsc(gain=.5)
s >> dac

# update
while True:
    s.freq = np.random.randint(30, 1000)
    now += 200 * ms
