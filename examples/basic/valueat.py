from pychuck import *

buf = SndBuf('data/kick.wav')
i = Impulse()
i >> dac

while True:
    pos = 0
    for _ in range(buf.samples()):
        i.next = buf.valueAt(pos)
        pos += 1
        now += 1 * samp

