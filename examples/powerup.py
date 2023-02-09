from pychuck import *


def main():
    import random

    # global noise source
    n = Noise()

    # sweep shred
    def sweep(st: float, inc: float, end: Time):
        # set up the audio chain
        n >> (z := TwoPole()) >> dac
        z.norm = 1
        z.gain = 0.1
        z.freq = st

        # store the time we entered the thread
        my_start = Time(now)
        my_seconds = 0.0

        z.radius = random.uniform(0.94, 0.99)

        # keep going until we 've passed the end time sent in by the control thread.
        while now < end:
            my_seconds = (now - my_start) / Dur(1, 's')
            z.gain = max(my_seconds * 4.0, 1.0) * 0.1
            z.freq = z.freq + inc * -0.02
            yield Dur(10, 'ms')

        n << z
        z << dac

    # time loop
    while True:
        d = Dur(500, 'ms')
        if random.randint(0, 10) > 3:
            d = d * 2.0
        if random.randint(0, 10) > 6:
            d = d * 3.0
        spork(sweep(220.0 * random.randint(1, 8),
                    880.0 + random.uniform(100.0, 880.0),
                    now + Dur(random.uniform(1.0, 3.0), 's')))
        yield d
