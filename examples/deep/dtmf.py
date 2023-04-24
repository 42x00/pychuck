from pychuck import *

row = SinOsc()
col = SinOsc()

row >= dac
col >= dac

cols = [1209.0, 1336.0, 1477.0]
rows = [697.0, 770.0, 852.0, 941.0]

i = 0
while i < 7:
    row.gain = .5
    col.gain = .5
    r = np.random.randint(0, 4)
    c = np.random.randint(0, 3)
    n = 1 + r * 3 + c

    if n == 11:
        n = 0
    if n == 10:
        print(r, c, '*')
    elif n == 12:
        print(r, c, '#')
    else:
        print(r, c, n)

    row.freq = rows[r]
    col.freq = cols[c]

    now += .1 * second
    row.gain = 0
    col.gain = 0
    now += .05 * second
    i += 1

