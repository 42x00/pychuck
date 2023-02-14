import queue
import threading
import types

import sounddevice as sd

import pychuck
from pychuck.module import _ADC, _DAC, _Blackhole
from pychuck.util import _ChuckTime, _code_transform


def spork(generator):
    current_shred = pychuck.__CHUCK__._current_shred
    current_shred._sporks.append(_ChuckShred(generator))
    pychuck.__CHUCK__._current_shred = current_shred


class _ChuckShred:
    def __init__(self, generator: types.GeneratorType = None):
        # content
        self._frames = 0
        self._modules = []
        self._sporks = []
        self._generator = generator
        # init
        if self._generator is not None and self._next():
            pychuck.__CHUCK__._shreds.append(self)

    def _next(self):
        pychuck.__CHUCK__._current_shred = self
        try:
            dur = next(self._generator)
            if dur._frames <= 0:
                raise ValueError("Duration must be greater than 0")
            self._frames = dur._frames
            return True
        except StopIteration:
            self._remove()
            return False

    def _remove(self):
        for shred in self._sporks:
            shred._remove()
        for module in self._modules:
            module._remove()

    def _update(self, frames: int):
        self._frames -= frames
        if self._frames == 0:
            if not self._next():
                pychuck.__CHUCK__._shreds._remove(self)


class _Chuck:
    def __init__(self, sample_rate: int = 22050, buffer_size: int = 64, verbose: bool = False):
        pychuck.__CHUCK__ = self
        # options
        self._sample_rate = sample_rate
        self._buffer_size = buffer_size
        self._verbose = verbose
        # stream
        self._stream = sd.Stream(samplerate=self._sample_rate, blocksize=self._buffer_size, channels=1, dtype='float32',
                                 callback=self._callback)
        self._ready = threading.Event()
        self._go = threading.Event()
        # shreds
        self._queue = queue.Queue()
        self._shreds = []
        self._current_shred = _ChuckShred()
        # global
        self._init_global()

    def _init_global(self):
        pychuck.now = _ChuckTime()
        pychuck.adc = _ADC()
        pychuck.dac = _DAC()
        pychuck.blackhole = _Blackhole()

    def _compute_graph(self, start: int, end: int):
        # un-compute
        for shred in self._shreds:
            for module in shred._modules:
                module._computed = False
        pychuck.dac._computed = False
        pychuck.blackhole._computed = False
        # compute
        for shred in self._shreds:
            for module in shred._modules:
                module._compute(start, end)

    def _callback(self, indata, outdata, frames, time, status):
        self._ready.wait()
        self._ready.clear()
        outdata[:, 0] = pychuck.dac.buffer
        pychuck.adc.buffer[:] = indata[:, 0]
        self._go.set()

    def start(self):
        print(f'Chuck:\n    sample_rate: {self._sample_rate}\n    buffer_size: {self._buffer_size}')
        self._ready.set()
        self._stream.start()
        while True:
            self._go.wait()
            self._go.clear()
            fi = 0
            frames_left = self._buffer_size
            while frames_left > 0:
                # add shreds
                while not self._queue.empty():
                    _ChuckShred(self._queue.get())
                # debug
                if self._verbose:
                    self._debug()
                # compute
                frames = self._get_min_shred_frames(frames_left)
                self._compute_graph(fi, fi + frames)
                # update
                for shred in self._shreds:
                    shred._update(frames)
                pychuck.now._frame += frames
                fi += frames
                frames_left -= frames
            self._ready.set()

    def add_shred(self, code: str):
        # TODO: check code
        exec(_code_transform(code), globals())
        self._queue.put(globals()["__chuck_shred__"]())

    def _debug(self):
        # shreds
        for shred in self._shreds:
            print(f'Shred {shred.shred_id}: {shred._frames} frames left')
        # graph
        print(f'{[module for module in self._dac._prev]} -> dac')

    def _get_min_shred_frames(self, frames_left: int) -> int:
        frames = frames_left
        for shred in self._shreds:
            if shred._frames < frames:
                frames = shred._frames
        return frames
