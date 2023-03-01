import queue
import threading
import types

import sounddevice as sd

import pychuck
from pychuck.module.base import _ADC, _DAC, _Blackhole
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

    def _compute_graph(self, frames: int):
        for shred in self._shreds:
            for module in shred._modules:
                module._computed = False
        pychuck.adc._computed = False
        pychuck.blackhole._compute(frames)
        pychuck.dac._compute(frames)

    def _callback(self, indata, outdata, frames, time, status):
        self._ready.wait()
        self._ready.clear()
        outdata[:, 0] = pychuck.dac.buffer
        pychuck.adc.buffer[:] = indata[:, 0]
        pychuck.adc._i = pychuck.dac._i = 0
        self._go.set()

    def start(self):
        print(f'Chuck:\n    sample_rate: {self._sample_rate}\n    buffer_size: {self._buffer_size}')
        self._ready.set()
        self._stream.start()
        while True:
            self._go.wait()
            self._go.clear()
            frames_left = self._buffer_size
            while frames_left > 0:
                # add shreds
                while not self._queue.empty():
                    _ChuckShred(self._queue.get())
                # compute
                frames = self._get_min_shred_frames(frames_left)
                self._compute_graph(frames)
                # update
                for shred in self._shreds:
                    shred._update(frames)
                pychuck.now._frame += frames
                frames_left -= frames
            self._ready.set()

    def add_shred(self, code: str):
        # TODO: check code
        exec(_code_transform(code), globals())
        self._queue.put(globals()["__chuck_shred__"]())

    def _get_min_shred_frames(self, frames_left: int) -> int:
        frames = frames_left
        for shred in self._shreds:
            if shred._frames < frames:
                frames = shred._frames
        return frames
