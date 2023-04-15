import numpy as np

import pychuck


class _ChuckModule:
    def __init__(self):
        pychuck.__CHUCK__._current_shred._modules.append(self)
        self._in_modules = []
        self._out_modules = []
        self._chuck_buffer_size = pychuck.__CHUCK__._buffer_size
        self._in_buffer = np.zeros(self._chuck_buffer_size)
        self._buffer = np.zeros(self._chuck_buffer_size)
        self._computed = False

    def __rshift__(self, other: '_ChuckModule'):
        self._out_modules.append(other)
        other._in_modules.append(self)
        return other

    def __lshift__(self, other: '_ChuckModule'):
        if self in other._in_modules:
            other._in_modules.remove(self)

    def _remove(self):
        for module in self._out_modules:
            module._in_modules.remove(self)
        for module in self._in_modules:
            module._out_modules.remove(self)

    def _aggregate_inputs(self, samples: int):
        self._in_buffer[:samples] = 0
        for module in self._in_modules:
            self._in_buffer[:samples] += module._compute_samples(samples)

    def _compute_samples(self, samples: int):
        if not self._computed:
            self._computed = True
            self._aggregate_inputs(samples)
            self._buffer[:samples] = self._compute(self._in_buffer[:samples])
        return self._buffer[:samples]

    def _compute(self, indata: np.ndarray):
        raise NotImplementedError


class _ADC(_ChuckModule):
    def __init__(self):
        super().__init__()
        self._i = 0

    def _compute_samples(self, samples: int):
        if not self._computed:
            self._computed = True
            self._i += samples
            self._i %= self._chuck_buffer_size
        return self._buffer[self._i - samples:self._i or None]


class _DAC(_ChuckModule):
    def __init__(self):
        super().__init__()
        self._i = 0

    def _compute_samples(self, samples: int):
        if not self._computed:
            self._computed = True
            self._aggregate_inputs(samples)
            self._buffer[self._i:self._i + samples] = self._in_buffer[:samples]
            self._i += samples
            self._i %= self._chuck_buffer_size
        return self._buffer[self._i - samples:self._i or None]


class _Blackhole(_ChuckModule):
    def _compute_samples(self, samples: int):
        if not self._computed:
            self._computed = True
            for module in self._in_modules:
                module._compute_samples(samples)

