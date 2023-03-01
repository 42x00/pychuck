import librosa
import numpy as np

from pychuck.module.base import _ChuckOutModule


class SinOsc(_ChuckOutModule):
    def __init__(self, freq: float = 440.0):
        super().__init__()
        self.freq = freq
        self.phase = -np.pi * 0.5

    def compute(self, frames: int):
        ret = librosa.tone(self.freq, sr=self._chuck_sample_rate, length=frames, phi=self.phase)
        self.phase += 2 * np.pi * self.freq * frames / self._chuck_sample_rate
        return ret


class SndBuf(_ChuckOutModule):
    def __init__(self, filename: str = None):
        super().__init__()
        self.data = None
        self.pos = 0
        self.gain = 1.0
        if filename:
            self.read(filename)

    def read(self, filename: str):
        self.data = librosa.load(filename, sr=self._chuck_sample_rate)[0]

    def compute(self, frames: int):
        self.pos += frames
        if self.pos >= len(self.data):
            self.pos = frames
        return self.data[self.pos - frames:self.pos] * self.gain
