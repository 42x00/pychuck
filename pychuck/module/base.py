import numpy as np

import pychuck


class _ChuckModule:
    def __init__(self):
        # global
        self._chuck_sample_rate = pychuck.__CHUCK__._sample_rate
        self._chuck_buffer_size = pychuck.__CHUCK__._buffer_size
        pychuck.__CHUCK__._current_shred._modules.append(self)
        # content
        self._computed = False
        self._in_modules = []
        self._in_buffer = None
        self.buffer = np.zeros(self._chuck_buffer_size, dtype=np.float32)
        self._i = 0

    def __rshift__(self, other: '_ChuckModule'):
        other._in_modules.append(self)
        return other

    def __lshift__(self, other: '_ChuckModule'):
        if self in other._in_modules:
            other._in_modules.remove(self)


class _Blackhole(_ChuckModule):
    def _compute(self, frames: int):
        for module in self._in_modules:
            module._compute(frames)


class _DAC(_ChuckModule):
    def _compute(self, frames: int):
        self.buffer[self._i:self._i + frames] = 0
        for module in self._in_modules:
            self.buffer[self._i:self._i + frames] += module._compute(frames)
        self._i += frames


class _ADC(_ChuckModule):
    def _compute(self, frames: int) -> np.ndarray:
        if not self._computed:
            self._computed = True
            self._i += frames
        return self.buffer[self._i - frames:self._i]


class _ChuckOutModule(_ChuckModule):
    def _compute(self, frames: int):
        if not self._computed:
            self._computed = True
            self.buffer[:frames] = self.compute(frames)
        return self.buffer[:frames]

    def compute(self, frames: int) -> np.ndarray:
        raise NotImplementedError


class _ChuckInOutModule(_ChuckModule):
    def __init__(self):
        super().__init__()
        self._in_buffer = np.zeros(self._chuck_buffer_size, dtype=np.float32)

    def _compute(self, frames: int):
        if not self._computed:
            self._computed = True

            self._in_buffer[:frames] = 0
            for module in self._in_modules:
                self._in_buffer[:frames] += module._compute(frames)

            self.buffer[:frames] = self.compute(self._in_buffer[:frames])

        return self.buffer[:frames]

    def compute(self, input: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class _ChuckBufferOutModule(_ChuckModule):
    def __init__(self):
        super().__init__()
        self.size = self._chuck_buffer_size

    def __setattr__(self, key, value):
        if key == 'size':
            self.buffer = np.zeros(2 * value, dtype=np.float32)
            self._i = 0
        super().__setattr__(key, value)

    def _compute(self, frames: int):
        if not self._computed:
            self._computed = True

            if self._i >= self.size:
                self.buffer[:self.size] = self.buffer[self.size:]
                self._i -= self.size

            self._i += frames

            if self._i >= self.size:
                self.buffer[self.size:] = self.compute()

        return self.buffer[self._i - frames:self._i]

    def compute(self) -> np.ndarray:
        raise NotImplementedError


class _ChuckBufferInOutModule(_ChuckModule):
    def __init__(self):
        super().__init__()
        self.size = self._chuck_buffer_size

    def __setattr__(self, key, value):
        if key == 'size':
            self._in_buffer = np.zeros(value + self._chuck_buffer_size, dtype=np.float32)
            self.buffer = np.zeros(2 * value, dtype=np.float32)
            self._i = 0
        super().__setattr__(key, value)

    def _compute(self, frames: int):
        if not self._computed:
            self._computed = True

            if self._i >= self.size:
                self.buffer[:self.size] = self.buffer[self.size:]
                self._in_buffer[:self._chuck_buffer_size] = self._in_buffer[self.size:]
                self._i -= self.size

            self._in_buffer[self._i:self._i + frames] = 0
            for module in self._in_modules:
                self._in_buffer[self._i:self._i + frames] += module._compute(frames)

            self._i += frames

            if self._i >= self.size:
                self.buffer[self.size:] = self.compute(self._in_buffer[:self.size])

        return self.buffer[self._i - frames:self._i]

    def compute(self, input: np.ndarray) -> np.ndarray:
        raise NotImplementedError
