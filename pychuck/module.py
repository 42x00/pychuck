import pychuck

import librosa
import numpy as np


class _ChuckModule:
    def __init__(self):
        self.now = pychuck.now
        self.sample_rate = pychuck.__CHUCK__.sample_rate
        self.buffer_size = pychuck.__CHUCK__.buffer_size
        self.buffer = np.zeros(self.buffer_size, dtype=np.float32)
        self.computed = False

    def __rshift__(self, other: '_ChuckModule'):
        self._next(other)
        other._prev(self)
        return other

    def _next(self, other: '_ChuckModule'):
        self.next.append(other)

    def _prev(self, other: '_ChuckModule'):
        self.prev.append(other)

    def clear(self):
        if not self.computed:
            return
        self.computed = False
        if hasattr(self, 'next'):
            for module in self.next:
                module.clear()
        if hasattr(self, 'prev'):
            for module in self.prev:
                module.clear()


class _ADC(_ChuckModule):
    def __init__(self):
        super().__init__()
        self.next = []

    def __repr__(self):
        return 'adc'

    def _next(self, other: '_ChuckModule'):
        pychuck.__CHUCK__.current_shred.modules['adc'].append(other)
        self.next.append(other)

    def compute(self, frames: int):
        if self.computed:
            return
        self.computed = True
        for module in self.next:
            module.compute(frames)


class _DAC(_ChuckModule):
    def __init__(self):
        super().__init__()
        self.prev = []

    def __repr__(self):
        return 'dac'

    def _prev(self, other: '_ChuckModule'):
        pychuck.__CHUCK__.current_shred.modules['dac'].append(other)
        self.prev.append(other)

    def compute(self, frames: int):
        if self.computed:
            return
        self.computed = True
        self.buffer.fill(0)
        for module in self.prev:
            module.compute(frames)
            self.buffer[:frames] += module.buffer[:frames]


class _Blackhole(_ChuckModule):
    def __init__(self):
        super().__init__()
        self.prev = []

    def __repr__(self):
        return 'blackhole'

    def _prev(self, other: '_ChuckModule'):
        pychuck.__CHUCK__.current_shred.modules['blackhole'].append(other)
        self.prev.append(other)

    def compute(self, frames: int):
        if self.computed:
            return
        self.computed = True
        for module in self.prev:
            module.compute(frames)


class SinOsc(_ChuckModule):
    def __init__(self, freq: float = 440.0):
        super().__init__()
        self.next = []
        self.freq = freq
        self.phi = -np.pi * 0.5

    def __repr__(self):
        return f"SinOsc(freq={self.freq:.2f})"

    def compute(self, frames: int):
        if self.computed:
            return
        self.computed = True
        self.buffer[:frames] = librosa.tone(self.freq, sr=self.sample_rate, length=frames, phi=self.phi)
        self.phi += 2 * np.pi * self.freq * frames / self.sample_rate
        for module in self.next:
            module.compute(frames)
