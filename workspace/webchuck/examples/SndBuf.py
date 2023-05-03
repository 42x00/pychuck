from pychuck import *

filename = 'snare.wav'

buf = SndBuf(path=filename)

buf >> dac

while True:
    buf.pos = 0
    buf.gain = np.random.uniform(.2, .5)
    now += 100 * ms
