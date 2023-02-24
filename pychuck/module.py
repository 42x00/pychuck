import torch
import librosa
import numpy as np

import pychuck


class _ChuckModule:
    def __init__(self):
        # global
        self._sample_rate = pychuck.__CHUCK__._sample_rate
        self._buffer_size = pychuck.__CHUCK__._buffer_size
        pychuck.__CHUCK__._current_shred._modules.append(self)
        # content
        self._computed = False
        self.buffer = np.zeros(self._buffer_size, dtype=np.float32)

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __rshift__(self, other: '_ChuckModule'):
        self._next.append(other)
        other._prev.append(self)
        return other

    def __lshift__(self, other: '_ChuckModule'):
        if other not in self._next:
            raise ValueError(f'{other} is not connected to {self}')
        self._next.remove(other)
        other._prev.remove(self)

    def _remove(self):
        if hasattr(self, '_next'):
            for module in self._next:
                module._prev._remove(self)
        if hasattr(self, '_prev'):
            for module in self._prev:
                module._next._remove(self)

    def compute(self, start: int, end: int):
        pass

    def _compute(self, start: int, end: int):
        if self._computed:
            return
        self._computed = True
        if hasattr(self, '_prev'):
            for module in self._prev:
                module._compute(start, end)
        self.compute(start, end)
        if hasattr(self, '_next'):
            for module in self._next:
                module._compute(start, end)


class _ChuckInModule(_ChuckModule):
    def __init__(self):
        super().__init__()
        self._prev = []


class _ChuckOutModule(_ChuckModule):
    def __init__(self):
        super().__init__()
        self._next = []


class _ChuckInOutModule(_ChuckModule):
    def __init__(self):
        super().__init__()
        self._prev = []
        self._next = []


class _ADC(_ChuckOutModule):
    def __init__(self):
        super().__init__()
        self._computed = True


class _DAC(_ChuckInModule):
    def compute(self, start: int, end: int):
        self.buffer.fill(0)
        for module in self._prev:
            self.buffer += module.buffer


class _Blackhole(_ChuckInModule):
    pass


class SinOsc(_ChuckOutModule):
    def __init__(self, freq: float = 440.0):
        super().__init__()
        self.freq = freq
        self.phi = -np.pi * 0.5

    def __repr__(self):
        return f"SinOsc(freq={self.freq:.2f})"

    def compute(self, start: int, end: int):
        length = end - start
        self.buffer[start:end] = librosa.tone(self.freq, sr=self._sample_rate, length=length, phi=self.phi)
        self.phi += 2 * np.pi * self.freq * length / self._sample_rate


class Noise(_ChuckOutModule):
    def compute(self, start: int, end: int):
        self.buffer[start:end] = np.random.uniform(-1, 1, end - start)


class TwoPole(_ChuckInOutModule):
    def __init__(self):
        super().__init__()
        self.norm = 0.0
        self.gain = 0.0
        self.freq = 0.0
        self.radius = 0.0

    def compute(self, start: int, end: int):
        self.buffer[:] = self._prev[0].buffer


class Rave(_ChuckInOutModule):
    def __init__(self):
        super().__init__()
        self._model = None
        self._size = 2048
        self._in = np.zeros(self._size + self._buffer_size, dtype=np.float32)
        self._out = np.zeros(2 * self._size, dtype=np.float32)
        self._fi = 0

    def _forward(self, x: np.ndarray):
        with torch.no_grad():
            return self._model.forward(
                torch.from_numpy(
                    x.reshape(1, 1, -1)
                )
            ).detach().numpy()[0][0]

    def load(self, model_path: str):
        self._model = torch.jit.load(model_path).eval()
        self._out[:self._size] = self._forward(self._in[:self._size])

    def compute(self, start: int, end: int):
        length = end - start

        self._in[self._fi:self._fi + length] = self._prev[0].buffer[start:end]

        if self._fi + length >= self._size:
            self._out[self._size:] = self._forward(self._in[:self._size])

        self.buffer[start:end] = self._out[self._fi:self._fi + length]

        self._fi += length
        if self._fi >= self._size:
            self._fi -= self._size
            self._in[:self._buffer_size] = self._in[self._size:]
            self._out[:self._size] = self._out[self._size:]
