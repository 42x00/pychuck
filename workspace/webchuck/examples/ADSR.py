from pychuck import *

s = SinOsc(freq=440, gain=0.5)
e = ADSR(A=10 * ms, D=8 * ms, S=.5, R=500 * ms)

s >> e >> dac

while True:
    s.freq = np.random.randint(100, 1000)
    e.keyOn()
    now += 500 * ms
    e.keyOff()
    now += e.releaseTime
    now += 300 * ms
