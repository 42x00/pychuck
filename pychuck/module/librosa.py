import wave
import librosa
import numpy as np

from pychuck.module.base import _ChuckOutModule, _ChuckInOutModule, _ChuckEnvelope
from pychuck.util import _ChuckDur


class Gain(_ChuckInOutModule):
    def __init__(self, gain: float = 1.0):
        super().__init__()
        self.gain = gain

    def compute(self, input: np.ndarray) -> np.ndarray:
        return input * self.gain


class SinOsc(_ChuckOutModule):
    def __init__(self, freq: float = 440.0, gain: float = 1.0):
        super().__init__()
        self.freq = freq
        self.gain = gain
        self.phase = -np.pi * 0.5
        self.last = 0

    def compute(self, frames: int):
        ret = librosa.tone(self.freq, sr=self._chuck_sample_rate, length=frames, phi=self.phase) * self.gain
        self.last = ret[-1]
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

    def samples(self) -> int:
        return len(self.data)

    def valueAt(self, pos: int) -> float:
        return self.data[pos]

    def compute(self, frames: int):
        self.pos += frames
        if self.pos >= len(self.data):
            self.pos = frames
        return self.data[self.pos - frames:self.pos] * self.gain


class Envelope(_ChuckEnvelope):
    def __init__(self):
        super().__init__()
        self.duration = _ChuckDur(self._chuck_sample_rate)

    def __setattr__(self, key, value):
        if key == "duration":
            frames = int(value._frames)

            self._sustain_i = frames
            self._release_i = self._sustain_i + self._chuck_buffer_size + 1
            self._off_i = self._release_i + frames

            self._envelope = np.concatenate((
                np.linspace(0, 1, frames),
                np.ones(self._chuck_buffer_size + 1),
                np.linspace(1, 0, frames),
                np.zeros(self._chuck_buffer_size)
            ))

            self._i = self._off_i

            self.__dict__["duration"] = value
        else:
            super().__setattr__(key, value)


class ADSR(_ChuckEnvelope):
    def __init__(self, A: _ChuckDur = None, D: _ChuckDur = None, S: float = None, R: _ChuckDur = None):
        super().__init__()
        self._release_samples = 0
        if A is not None and D is not None and S is not None and R is not None:
            self.set(A, D, S, R)

    def set(self, A: _ChuckDur, D: _ChuckDur, S: float, R: _ChuckDur):
        A_frames, D_frames, R_frames = int(A._frames), int(D._frames), int(R._frames)

        self._sustain_i = A_frames + D_frames
        self._release_i = self._sustain_i + self._chuck_buffer_size + 1
        self._off_i = self._release_i + R_frames

        self._release_samples = R._frames

        self._envelope = np.concatenate((
            np.linspace(0, 1, A_frames),
            np.linspace(1, S, D_frames),
            np.ones(self._chuck_buffer_size + 1) * S,
            np.linspace(S, 0, R_frames),
            np.zeros(self._chuck_buffer_size)
        ))

        self._i = self._off_i

    def releaseTime(self) -> _ChuckDur:
        return _ChuckDur(self._release_samples)


class Delay(_ChuckInOutModule):
    def __init__(self, delay: _ChuckDur = _ChuckDur(0), gain: float = 1.0):
        super().__init__()
        self.gain = gain
        self._delay_frames = 0
        self._buffer = None
        self.delay = delay

    def __setattr__(self, key, value):
        if key == "delay":
            self._delay_frames = int(value._frames)
            self._buffer = np.zeros(self._delay_frames + self._chuck_buffer_size, dtype=np.float32)
            self.__dict__["delay"] = value
        else:
            super().__setattr__(key, value)

    def compute(self, input: np.ndarray) -> np.ndarray:
        frames = len(input)
        self._buffer[self._delay_frames:self._delay_frames + frames] = input
        res = self._buffer[:frames].copy()
        self._buffer[:self._delay_frames] = self._buffer[frames:self._delay_frames + frames]
        return res * self.gain


class Impulse(_ChuckOutModule):
    def __init__(self, gain: float = 1.0):
        super().__init__()
        self.gain = gain
        self.next = 0

    def compute(self, frames: int):
        res = np.zeros(frames, dtype=np.float32)
        res[0] = self.next * self.gain
        self.next = 0
        return res


class Step(_ChuckOutModule):
    def __init__(self, gain: float = 1.0):
        super().__init__()
        self.gain = gain
        self.next = 0

    def compute(self, frames: int):
        return np.zeros(frames, dtype=np.float32) + self.next * self.gain


class Noise(_ChuckOutModule):
    def compute(self, frames: int):
        return np.random.uniform(-1, 1, frames)
