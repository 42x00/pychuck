from pychuck import *

n = Noise()
e = Envelope()

n >> e >> dac

while True:
    e.duration = t = np.random.uniform(10, 500) * ms
    print(f'rise/fall: {t / ms} ms')
    e.keyOn()
    now += 800 * ms
    e.keyOff()
    now += 800 * ms
