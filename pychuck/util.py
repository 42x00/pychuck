import pychuck

from enum import Enum


class _ChuckDurUnit(Enum):
    ms = 1e-3
    s = 1
    m = 60
    h = 3600
    day = 86400
    week = 604800


class Dur:
    def __init__(self, dur: float, unit: str = 's'):
        self.frames = dur * pychuck.__CHUCK__.sample_rate
        if unit == 'samp':
            self.frames = int(dur)
        elif unit in _ChuckDurUnit.__members__:
            self.frames = int(self.frames * _ChuckDurUnit[unit].value)
        else:
            raise ValueError(f'Invalid time unit: {unit}')
        if self.frames <= 0:
            raise ValueError(f'Duration must be positive, but got {dur} {unit}')


class _ChuckNow:
    def __init__(self):
        self.frame = 0
