from pychuck import *

s = SinOsc(gain=.5)
e = ADSR(A=10 * ms, D=8 * ms, S=.5, R=500 * ms)

s >= e >= dac

while True:
    s.freq = Std.mtof(np.random.randint(32, 96))
    e.keyOn()
    now += 500 * ms
    e.keyOff()
    now += e.releaseTime
    now += 300 * ms
