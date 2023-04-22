import numpy as np

import pychuck


class UGen:
    def __init__(self):
        pychuck.__CHUCK__._current_shred._modules.append(self)
        self.chan = [self]
        self.gain = 1
        self._sample_rate = pychuck.__CHUCK__._sample_rate
        self._buffer_size = pychuck.__CHUCK__._buffer_size
        self._in_buffer = np.zeros(self._buffer_size, dtype=np.float32)
        self._buffer = np.zeros(self._buffer_size, dtype=np.float32)
        self._computed = False
        self._in_modules = []
        self._out_modules = []

    def __ge__(self, other: 'UGen'):
        if len(self.chan) == len(other.chan):
            for i in range(len(self.chan)):
                self.chan[i]._out_modules.append(other.chan[i])
                other.chan[i]._in_modules.append(self.chan[i])
        else:
            for self_chan in self.chan:
                for other_chan in other.chan:
                    self_chan._out_modules.append(other_chan)
                    other_chan._in_modules.append(self_chan)

    def __le__(self, other: 'UGen'):
        for self_chan in self.chan:
            for other_chan in other.chan:
                if self_chan in other_chan._in_modules:
                    other_chan._in_modules.remove(self_chan)

    def _remove(self):
        for module in self._out_modules:
            module._in_modules.remove(self)
        for module in self._in_modules:
            module._out_modules.remove(self)

    def _aggreate_inputs(self, samples: int):
        self._in_buffer[:samples] = 0
        for module in self._in_modules:
            self._in_buffer[:samples] += module._compute_samples(samples)

    def _compute_samples(self, samples: int) -> np.ndarray:
        if not self._computed:
            self._computed = True
            self._aggreate_inputs(samples)
            self._compute(samples)
        return self._buffer[:samples]

    def _compute(self, samples: int):
        for i in range(samples):
            self._buffer[i] = self._tick(self._in_buffer[i])

    def _tick(self, in_sample: float) -> float:
        raise NotImplementedError


class _Blackhole(UGen):
    def _compute_samples(self, samples: int) -> np.ndarray:
        if not self._computed:
            self._computed = True
            for module in self._in_modules:
                module._compute_samples(samples)
        return self._buffer[:samples]


class _ADCChannel(UGen):
    def __init__(self):
        super().__init__()
        self._i = 0

    def _compute_samples(self, samples: int) -> np.ndarray:
        if not self._computed:
            self._computed = True
            self._i = (self._i + samples) % self._buffer_size
        return self._buffer[self._i - samples:self._i or None]


class _ADC(UGen):
    def __init__(self):
        super().__init__()
        self.chan = [_ADCChannel() for _ in range(pychuck.__CHUCK__._in_channels)]

    def __getattr__(self, item):
        if item == 'left':
            return self.chan[0]
        elif item == 'right':
            return self.chan[1]
        else:
            raise AttributeError

    def _set(self, indata: np.ndarray):
        for i in range(len(self.chan)):
            self.chan[i]._buffer[:] = indata[:, i]


class _DACChannel(UGen):
    def __init__(self):
        super().__init__()
        self._i = 0

    def _compute_samples(self, samples: int) -> np.ndarray:
        if not self._computed:
            self._computed = True
            self._aggreate_inputs(samples)
            self._buffer[self._i:self._i + samples] = self._in_buffer[:samples]
            self._i = (self._i + samples) % self._buffer_size
        return self._buffer[self._i - samples:self._i or None]


class _DAC(UGen):
    def __init__(self):
        super().__init__()
        self.chan = [_DACChannel() for _ in range(pychuck.__CHUCK__._out_channels)]

    def __getattr__(self, item):
        if item == 'left':
            return self.chan[0]
        elif item == 'right':
            return self.chan[1]
        else:
            raise AttributeError

    def _compute_samples(self, samples: int) -> np.ndarray:
        for chan in self.chan:
            chan._compute_samples(samples)

    def _get(self) -> np.ndarray:
        return np.stack([chan._buffer for chan in self.chan], axis=1)


class Impulse(UGen):
    def __init__(self):
        super().__init__()
        self.next = 0

    def _compute(self, samples: int):
        self._buffer[0] = self.next
        self.next = 0
