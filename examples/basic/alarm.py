from pychuck import *

T = Dur(2, second)

start = now.copy()
later = now + T

while now < later:
    print(f'{(T - (now - start)) / second} left...')
    Dur(1, second) >> now

(s := SinOsc(freq=880)) >> dac

while True:
    s.gain = 1.0
    Dur(300, ms) >> now
    s.gain = 0.0
    Dur(300, ms) >> now
