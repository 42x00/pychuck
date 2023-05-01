import queue
import types

import numpy as np

from .module import _ADC, _DAC, _Blackhole
from .util import _ChuckDur, _ChuckTime, _wrap_code, _load_stk


class _ChuckShred:
    def __init__(self, VM: '_Chuck', generator: types.GeneratorType = None):
        self._generator = generator
        self._samples_left = 0
        self._modules = []
        self._sporks = []
        if generator is not None and self._next(VM=VM):
            VM._shreds.append(self)

    def _next(self, VM: '_Chuck') -> bool:
        try:
            VM._current_shred = self
            dur = next(self._generator)
            if dur._samples < 0:
                raise ValueError('Duration must be positive')
            self._samples_left = int(dur._samples)
            return True
        except StopIteration:
            return False

    def _update(self, samples: int, VM: '_Chuck'):
        self._samples_left -= samples
        if self._samples_left <= 0:
            if not self._next(VM=VM):
                self._remove(VM=VM)

    def _remove(self, VM: '_Chuck'):
        for shred in self._sporks:
            shred._remove(VM=VM)
        self._sporks.clear()
        for module in self._modules:
            module._remove()
        self._modules.clear()
        if self in VM._shreds:
            VM._shreds.remove(self)


class _Chuck:
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 256, in_channels: int = 1, out_channels: int = 2,
                 compile: bool = False):
        self._sample_rate = sample_rate
        self._buffer_size = buffer_size
        self._in_channels = in_channels
        self._out_channels = out_channels
        self._shreds = []
        self._global_shred = _ChuckShred(VM=self)
        self._current_shred = self._global_shred
        self._command_queue = queue.Queue()
        self._libstk_wrapper = _load_stk(compile=compile)

        self._adc = _ADC(VM=self)
        self._dac = _DAC(VM=self)
        self._blackhole = _Blackhole(VM=self)
        self._now = _ChuckTime(0)
        self._samp = _ChuckDur(1)
        self._second = _ChuckDur(self._sample_rate)
        self._ms = self._second / 1000
        self._minute = self._second * 60
        self._hour = self._minute * 60
        self._day = self._hour * 24
        self._week = self._day * 7

    def _forward(self, indata: np.ndarray) -> np.ndarray:
        self._adc._set(indata)

        while not self._command_queue.empty():
            self._run(self._command_queue.get())

        samples_left = len(indata)
        while samples_left > 0:
            samples = min([samples_left] + [shred._samples_left for shred in self._shreds])
            self._compute(samples)
            samples_left -= samples
            self._now._sample += samples
            for shred in self._shreds:
                shred._update(samples, VM=self)

        return self._dac._get()

    def _run(self, args):
        if args[0] == 'add_shred':
            _ChuckShred(VM=self, generator=args[1])
        elif args[0] == 'remove_last_shred':
            if len(self._shreds) > 0:
                self._shreds[-1]._remove(VM=self)

    def _compute(self, samples: int):
        for shred in self._shreds:
            for module in shred._modules:
                module._computed = False
        for module in self._global_shred._modules:
            module._computed = False
        self._blackhole._compute_samples(samples)
        self._dac._compute_samples(samples)

    def _add_shred(self, code: str):
        exec(_wrap_code(code), globals())
        self._command_queue.put(['add_shred', globals()['__chuck_shred__'](
            self, self._adc, self._dac, self._blackhole, self._now,
            self._samp, self._ms, self._second, self._minute, self._hour, self._day, self._week
        )])

    def _remove_last_shred(self):
        self._command_queue.put(['remove_last_shred'])

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
