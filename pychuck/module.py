import pychuck

import librosa
import threading
from enum import Enum
import numpy as np
import sounddevice as sd


class _ChuckModuleType(Enum):
    IN = 0  # dac, blackhole, etc.
    OUT = 1  # adc, SinOsc, etc.
    IN_OUT = 2  # FFT, etc.


class _ChuckModule:
    def __init__(self):
        self.type = None
        self.now = pychuck.__CHUCK__.now
        self.sample_rate = pychuck.__CHUCK__.sample_rate
        self.buffer_size = pychuck.__CHUCK__.buffer_size
        # self.prev = []
        # self.next = []

    def __rshift__(self, other: '_ChuckModule') -> '_ChuckModule':
        if self.type == _ChuckModuleType.IN:
            raise Exception(f'{self.__class__.__name__} cannot be used as an input')
        elif other.type == _ChuckModuleType.OUT:
            raise Exception(f'{other.__class__.__name__} cannot be used as an output')
        else:
            return self.connect(other)

    def append(self, other: '_ChuckModule', which: str):
        self.__dict__[which].append(other)

    def connect(self, other: '_ChuckModule') -> '_ChuckModule':
        self.append(other, 'next')
        other.append(self, 'prev')
        return other


class _ChuckGlobalModule(_ChuckModule):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.modules = []
        self.stream = None

    def append(self, other: '_ChuckModule', which: str):
        with self.lock:
            self.modules.append(other)
            if not self.stream.active:
                self.stream.start()
        threading.current_thread().instance.remember(self, other)

    def remove(self, other: '_ChuckModule'):
        with self.lock:
            self.modules.remove(other)
            if len(self.modules) == 0 and self.stream.active:
                self.stream.stop()


class _ADC(_ChuckGlobalModule):
    def __init__(self):
        super().__init__()
        self.type = _ChuckModuleType.OUT

    def __str__(self):
        return 'adc'

    def compute(self, length: int):
        # TODO: implement
        pass


class _DAC(_ChuckGlobalModule):
    def __init__(self):
        super().__init__()
        self.type = _ChuckModuleType.IN

        self.ready = threading.Event()
        self.go = threading.Event()
        self.buffer = np.zeros(self.buffer_size * 2, dtype=np.float32)
        self.i = 0

        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            channels=1,
            dtype=np.float32,
            callback=self.callback)

    def __str__(self):
        return 'dac'

    def callback(self, outdata, frames, time, status):
        # wait for chuck
        self.ready.wait()
        # copy
        outdata[:] = self.buffer[:frames].reshape(-1, 1)
        # roll
        self.i -= frames
        self.buffer[:self.i] = self.buffer[frames:frames + self.i]
        # notify chuck
        self.ready.clear()
        self.go.set()

    def compute(self, length: int):
        self.buffer[self.i:self.i + length] = 0
        for module in self.modules:
            self.buffer[self.i:self.i + length] += module.compute(length)
        self.i += length
        if self.i >= self.buffer_size:
            self.ready.set()
            self.go.wait()
            self.go.clear()

    def debug(self):
        print([str(module) for module in self.modules])


class _Blackhole(_ChuckGlobalModule):
    def __init__(self):
        super().__init__()
        self.type = _ChuckModuleType.IN

    def __str__(self):
        return 'blackhole'

    def compute(self, length: int):
        # TODO: implement
        pass


class SinOsc(_ChuckModule):
    def __init__(self, freq: float = 440):
        super().__init__()
        self.type = _ChuckModuleType.OUT
        self.next = []
        self.freq = freq

    def __str__(self):
        return f'SinOsc({self.freq})'

    def compute(self, length: int):
        phi = self.now.sample_count / self.sample_rate * 2 * np.pi * self.freq
        output = librosa.tone(self.freq, sr=self.sample_rate, length=length, phi=phi)
        return output


class SndBuf(_ChuckModule):
    def __init__(self, filename: str = None):
        super().__init__()
        self.type = _ChuckModuleType.OUT
        self.next = []
        self.filename = filename
        self.data = None
        self.pos = 0

    def __str__(self):
        return f'SndBuf({self.filename.split("/")[-1]})'

    def read(self, filename: str):
        self.filename = filename
        self.data, _ = librosa.load(filename, sr=self.sample_rate)
        self.pos = 0

    def compute(self, length: int):
        output = np.zeros(length, dtype=np.float32)
        if self.pos > len(self.data):
            return output
        output[:len(self.data) - self.pos] = self.data[self.pos:self.pos + length]
        self.pos += length
