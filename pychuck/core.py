import pychuck
from pychuck.module import _ADC, _DAC, _Blackhole
from pychuck.util import _ChuckTime, _code2gen

import types
import queue
import threading
import sounddevice as sd


def spork(generator):
    current_shred = pychuck.__CHUCK__.current_shred
    current_shred.sporks.append(_ChuckShred(generator))
    pychuck.__CHUCK__.current_shred = current_shred


class _ChuckShred:
    def __init__(self, code_or_gen: str or types.GeneratorType = None):
        # content
        self.shred_id = pychuck.__CHUCK__.get_shred_id()
        self.frames = 0
        self.modules = []
        self.sporks = []
        # init
        self.generator = _code2gen(code_or_gen, self.shred_id)
        if self.next():
            pychuck.__CHUCK__.shreds.append(self)

    def next(self):
        pychuck.__CHUCK__.current_shred = self
        try:
            dur = next(self.generator)
            if dur.frames <= 0:
                raise ValueError("Duration must be greater than 0")
            self.frames = dur.frames
            return True
        except (StopIteration, TypeError):
            self.remove()
            return False

    def remove(self):
        for shred in self.sporks:
            shred.remove()
        for module in self.modules:
            module._remove()

    def update(self, frames: int):
        self.frames -= frames
        if self.frames == 0:
            if not self.next():
                pychuck.__CHUCK__.shreds.remove(self)

    def uncompute_modules(self):
        for module in self.modules:
            module._computed = False

    def compute_modules(self, start: int, end: int):
        for module in self.modules:
            module._compute(start, end)


class _Chuck:
    def __init__(self, sample_rate: int = 22050, buffer_size: int = 64, verbose: bool = False):
        pychuck.__CHUCK__ = self
        # options
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.verbose = verbose
        # stream
        self.stream = sd.Stream(samplerate=self.sample_rate, blocksize=self.buffer_size, channels=1, dtype='float32',
                                callback=self.callback)
        self.ready = threading.Event()
        self.go = threading.Event()
        # shreds
        self.queue = queue.Queue()
        self.shreds = []
        self.shred_id = 0
        self.shred = _ChuckShred()
        self.current_shred = self.shred
        # global
        pychuck.now = self.now = _ChuckTime()
        pychuck.adc = self.adc = _ADC()
        pychuck.dac = self.dac = _DAC()
        pychuck.blackhole = self.blackhole = _Blackhole()

    def get_shred_id(self):
        self.shred_id += 1
        return self.shred_id - 1

    def compute_graph(self, start: int, end: int):
        # un-compute
        for shred in self.shreds:
            shred.uncompute_modules()
        self.shred.uncompute_modules()
        # compute
        self.shred.compute_modules(start, end)

    def callback(self, indata, outdata, frames, time, status):
        self.ready.wait()
        self.ready.clear()
        outdata[:, 0] = self.dac.buffer
        self.adc.buffer[:] = indata[:, 0]
        self.go.set()

    def start(self):
        print(f'Chuck:\n    sample_rate: {self.sample_rate}\n    buffer_size: {self.buffer_size}')
        self.ready.set()
        self.stream.start()
        while True:
            self.go.wait()
            self.go.clear()
            fi = 0
            frames_left = self.buffer_size
            while frames_left > 0:
                # add shreds
                while not self.queue.empty():
                    _ChuckShred(self.queue.get_nowait())
                # debug
                if self.verbose:
                    self.debug()
                # compute
                frames = min(frames_left, min(shred.frames for shred in self.shreds))
                self.compute_graph(fi, fi + frames)
                # update
                for shred in self.shreds:
                    shred.update(frames)
                self.now.frame += frames
                fi += frames
                frames_left -= frames
            self.ready.set()

    def add_shred(self, code: str):
        self.queue.put_nowait(code)

    def debug(self):
        # shreds
        for shred in self.shreds:
            print(f'Shred {shred.shred_id}: {shred.frames} frames left')
        # graph
        print(f'{[module for module in self.dac._prev]} -> dac')
