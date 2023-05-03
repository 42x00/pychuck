from pychuck import *

s = SinOsc(freq=440, gain=0.5)
s >> dac

while True:
    s.freq = np.random.randint(100, 1000)
    now += 200 * ms
