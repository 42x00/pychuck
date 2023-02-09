import pychuck

import librosa
import numpy as np
from enum import Enum


class _ChuckModuleType(Enum):
    IN = 0  # dac, blackhole, etc.
    OUT = 1  # adc, SinOsc, etc.
    IN_OUT = 2  # FFT, etc.


class _ChuckModule:
    def __init__(self):
        # global
        self._now = pychuck.now
        self._sample_rate = pychuck.__CHUCK__.sample_rate
        self._buffer_size = pychuck.__CHUCK__.buffer_size
        pychuck.__CHUCK__.current_shred.modules.append(self)
        # content
        self._type = None
        self._computed = False
        self.buffer = np.zeros(self._buffer_size, dtype=np.float32)

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __rshift__(self, other: '_ChuckModule'):
        if self._type == _ChuckModuleType.IN or other._type == _ChuckModuleType.OUT:
            raise TypeError(f'Cannot connect {self} to {other}')
        self._next.append(other)
        other._prev.append(self)
        return other

    def __lshift__(self, other: '_ChuckModule'):
        if self._type == _ChuckModuleType.IN or other._type == _ChuckModuleType.OUT:
            raise TypeError(f'Cannot disconnect {self} from {other}')
        self._next.remove(other)
        other._prev.remove(self)

    def _update_type(self, type_: _ChuckModuleType):
        self._type = type_
        if self._type != _ChuckModuleType.IN:
            self._next = []
        if self._type != _ChuckModuleType.OUT:
            self._prev = []

    def _remove(self):
        if self._type != _ChuckModuleType.IN:
            for module in self._next:
                module._prev.remove(self)
        if self._type != _ChuckModuleType.OUT:
            for module in self._prev:
                module._next.remove(self)

    def compute(self, start: int, end: int):
        pass

    def _compute(self, start: int, end: int):
        if self._computed:
            return
        self._computed = True
        if self._type != _ChuckModuleType.OUT:
            for module in self._prev:
                module._compute(start, end)
        self.compute(start, end)
        if self._type != _ChuckModuleType.IN:
            for module in self._next:
                module._compute(start, end)


class _ADC(_ChuckModule):
    def __init__(self):
        super().__init__()
        self._update_type(_ChuckModuleType.OUT)


class _DAC(_ChuckModule):
    def __init__(self):
        super().__init__()
        self._update_type(_ChuckModuleType.IN)

    def compute(self, start: int, end: int):
        self.buffer.fill(0)
        for module in self._prev:
            self.buffer += module.buffer


class _Blackhole(_ChuckModule):
    def __init__(self):
        super().__init__()
        self._update_type(_ChuckModuleType.IN)


class SinOsc(_ChuckModule):
    def __init__(self, freq: float = 440.0):
        super().__init__()
        self._update_type(_ChuckModuleType.OUT)

        self.freq = freq
        self.phi = -np.pi * 0.5

    def __repr__(self):
        return f"SinOsc(freq={self.freq:.2f})"

    def compute(self, start: int, end: int):
        length = end - start
        self.buffer[start:end] = librosa.tone(self.freq, sr=self._sample_rate, length=length, phi=self.phi)
        self.phi += 2 * np.pi * self.freq * length / self._sample_rate


class Noise(_ChuckModule):
    def __init__(self):
        super().__init__()
        self._update_type(_ChuckModuleType.OUT)

    def compute(self, start: int, end: int):
        self.buffer[start:end] = np.random.uniform(-1, 1, end - start)


class TwoPole(_ChuckModule):
    def __init__(self):
        super().__init__()
        self._update_type(_ChuckModuleType.IN_OUT)

        self.norm = 0.0
        self.gain = 0.0
        self.freq = 0.0
        self.radius = 0.0
