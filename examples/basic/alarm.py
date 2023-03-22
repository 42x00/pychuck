from pychuck import *

T = 2 * second

start = now.copy()
later = now + T

while now < later:
    print(f'{(T - (now - start)) / second} left...')
    now += 1 * second

s = SinOsc(freq=880)
# s >> JCRev(mix=.025) >> dac
s >> dac

while True:
    s.gain = 1.0
    now += 300 * ms
    s.gain = 0.0
    now += 300 * ms
