import asyncio
import queue
import sys
import types

import numpy as np

import pychuck
from pychuck.io import main
from pychuck.module import _ADC, _DAC, _Blackhole
from pychuck.util import _ChuckDur, _ChuckTime, _code_transform


class _ChuckShred:
    def __init__(self, generator: types.GeneratorType = None):
        self._generator = generator
        self._samples_left = 0
        self._modules = []
        if self._generator is not None and self._next():
            pychuck.__CHUCK__._shreds.append(self)

    def _next(self):
        pychuck.__CHUCK__._current_shred = self
        try:
            dur = next(self._generator)
            if dur._samples < 0:
                raise ValueError('Duration must be positive')
            self._samples_left = int(dur._samples)
            return True
        except StopIteration:
            return False

    def _remove(self):
        for module in self._modules:
            module._remove()
        pychuck.__CHUCK__._shreds.remove(self)


class _Chuck:
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 256, verbose: bool = False):
        pychuck.__CHUCK__ = self
        # parameters
        self._sample_rate = sample_rate
        self._buffer_size = buffer_size
        self._verbose = verbose
        # shreds
        self._shred_queue = queue.Queue()
        self._shreds = []
        self._global_shred = _ChuckShred()
        self._current_shred = self._global_shred
        # global
        self._init_global()

    def _init_global(self):
        pychuck.adc = _ADC()
        pychuck.dac = _DAC()
        pychuck.blackhole = _Blackhole()
        pychuck.now = _ChuckTime(0)
        pychuck.samp = _ChuckDur(1)
        pychuck.second = _ChuckDur(self._sample_rate)
        pychuck.ms = pychuck.second / 1000
        pychuck.minute = pychuck.second * 60
        pychuck.hour = pychuck.minute * 60
        pychuck.day = pychuck.hour * 24
        pychuck.week = pychuck.day * 7

    def _compute(self, samples: int):
        for shred in self._shreds:
            for module in shred._modules:
                module._computed = False
        for module in self._global_shred._modules:
            module._computed = False
        pychuck.blackhole._compute_samples(samples)
        pychuck.dac._compute_samples(samples)

    def _compute_buffer(self, indata: np.ndarray):
        pychuck.adc._buffer[:] = indata[:, 0]

        while not self._shred_queue.empty():
            _ChuckShred(self._shred_queue.get())

        samples_left = self._buffer_size
        while samples_left > 0:
            samples = min([samples_left] + [shred._samples_left for shred in self._shreds])
            self._compute(samples)

            samples_left -= samples
            pychuck.now._sample += samples

            for shred in self._shreds:
                shred._samples_left -= samples
                if shred._samples_left == 0:
                    if not shred._next():
                        shred._remove()

        return pychuck.dac._buffer[:, np.newaxis]

    def _start(self):
        try:
            asyncio.run(main(sample_rate=self._sample_rate, buffer_size=self._buffer_size,
                             callback=self._compute_buffer))
        except KeyboardInterrupt:
            sys.exit('\nInterrupted by user')

    def _add_shred(self, code: str):
        exec(_code_transform(code), globals())
        self._shred_queue.put(globals()['__chuck_shred__']())
