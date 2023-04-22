import numpy as np

import pychuck


class _ADC:
    def _set(self, indata: np.ndarray):
        self._buffer = indata


class _DAC:
    def __init__(self):
        self._buffer = np.zeros(pychuck.__CHUCK__._buffer_size)

    def _get(self) -> np.ndarray:
        return self._buffer
