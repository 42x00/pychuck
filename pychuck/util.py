import pychuck

import threading
from enum import Enum


class _ChuckNow:
    def __init__(self):
        self.sample_count = 0

    def reset(self):
        self.sample_count = 0


class _ChuckTimeUnit(Enum):
    ms = 1e-3
    s = 1
    m = 60
    h = 3600


class Dur:
    def __init__(self, value: float, unit: str = 's'):
        self.value = value * pychuck.__CHUCK__.sample_rate
        if unit == 'samp':
            self.value = value
        elif unit in _ChuckTimeUnit.__members__:
            self.value *= _ChuckTimeUnit[unit].value
        else:
            raise ValueError(f'Invalid time unit: {unit}')

    def __rshift__(self, other: _ChuckNow):
        sample_request = int(round(self.value))
        if sample_request > 0:
            threading.current_thread().instance.wait(sample_request)
