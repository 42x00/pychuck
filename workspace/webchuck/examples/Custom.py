from pychuck import *


class Custom(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min = -1
        self.max = 1

    def _compute(self, samples: int):
        self._buffer[:samples] = np.random.uniform(self.min, self.max, samples)


n = Custom(gain=0.1)
n >> dac

now += 1 * second
