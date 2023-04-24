import queue
import types

import numpy as np

import pychuck
from pychuck.module import _ADC, _DAC, _Blackhole
from pychuck.util import _ChuckDur, _ChuckTime, _wrap_code, _load_stk


def spork(generator: types.GeneratorType):
    current_shred = pychuck.__CHUCK__._current_shred
    current_shred._sporks.append(_ChuckShred(generator))
    pychuck.__CHUCK__._current_shred = current_shred


class _ChuckShred:
    def __init__(self, generator: types.GeneratorType = None):
        self._generator = generator
        self._samples_left = 0
        self._modules = []
        self._sporks = []
        if generator is not None and self._next():
            pychuck.__CHUCK__._shreds.append(self)

    def _next(self):
        try:
            pychuck.__CHUCK__._current_shred = self
            dur = next(self._generator)
            if dur._samples < 0:
                raise ValueError('Duration must be positive')
            self._samples_left = int(dur._samples)
            return True
        except StopIteration:
            return False

    def _update(self, samples: int):
        self._samples_left -= samples
        if self._samples_left <= 0:
            if not self._next():
                self._remove()

    def _remove(self):
        for shred in self._sporks:
            shred._remove()
        self._sporks.clear()
        for module in self._modules:
            module._remove()
        self._modules.clear()
        if self in pychuck.__CHUCK__._shreds:
            pychuck.__CHUCK__._shreds.remove(self)


class _Chuck:
    def __init__(self, compile: bool = False):
        pychuck.__CHUCK__ = self
        self._sample_rate = 44100
        self._buffer_size = 256
        self._in_channels = 1
        self._out_channels = 2
        self._shreds = []
        self._global_shred = _ChuckShred()
        self._current_shred = self._global_shred
        self._command_queue = queue.Queue()
        self._init_globals()
        self._libstk_wrapper = _load_stk(compile=compile)

    def _init_globals(self):
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

    def _forward(self, indata: np.ndarray) -> np.ndarray:
        pychuck.adc._set(indata)

        while not self._command_queue.empty():
            self._run(self._command_queue.get())

        samples_left = len(indata)
        while samples_left > 0:
            samples = min([samples_left] + [shred._samples_left for shred in self._shreds])
            self._compute(samples)
            samples_left -= samples
            pychuck.now._sample += samples
            for shred in self._shreds:
                shred._update(samples)

        return pychuck.dac._get()

    def _run(self, args):
        if args[0] == 'add_shred':
            _ChuckShred(args[1])

    def _compute(self, samples: int):
        for shred in self._shreds:
            for module in shred._modules:
                module._computed = False
        for module in self._global_shred._modules:
            module._computed = False
        pychuck.blackhole._compute_samples(samples)
        pychuck.dac._compute_samples(samples)

    def _add_shred(self, code: str):
        exec(_wrap_code(code), globals())
        self._command_queue.put(['add_shred', globals()['__chuck_shred__']()])

    def _loop(self):
        from pychuck.io import main
        import asyncio
        import sys
        try:
            asyncio.run(main(sample_rate=self._sample_rate, buffer_size=self._buffer_size,
                             channels=(self._in_channels, self._out_channels),
                             callback=self._forward))
        except KeyboardInterrupt:
            sys.exit('\nInterrupted by user')
