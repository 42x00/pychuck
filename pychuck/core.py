import pychuck
from pychuck.module import _ADC, _DAC, _Blackhole
from pychuck.util import _ChuckNow, _code_transform

import queue
import threading
import numpy as np
import sounddevice as sd


def spork(obj):
    pychuck.__CHUCK__.queue.put_nowait(obj)


class _ChuckShred:
    def __init__(self, obj):
        self.modules = {'adc': [], 'dac': [], 'blackhole': []}

        if isinstance(obj, str):
            obj = self.filepath2generator(obj)
        self.generator = obj()

        dur = self.next()
        if dur is None:
            self.disconnect()
        else:
            self.frames = dur.frames
            pychuck.__CHUCK__.shreds.append(self)

    def disconnect(self):
        for module in self.modules['adc']:
            pychuck.adc.next.remove(module)
        for module in self.modules['dac']:
            pychuck.dac.prev.remove(module)
        for module in self.modules['blackhole']:
            pychuck.blackhole.prev.remove(module)

    def update(self, frames: int):
        self.frames -= frames
        if self.frames == 0:
            dur = self.next()
            if dur is None:
                self.disconnect()
                pychuck.__CHUCK__.shreds.remove(self)
            else:
                self.frames = dur.frames

    def next(self):
        pychuck.__CHUCK__.current_shred = self
        while True:
            try:
                dur = next(self.generator)
                if dur is None:
                    continue
                return dur
            except StopIteration:
                return None

    def filepath2generator(self, filepath):
        pychuck.__CHUCK__.current_shred = self
        shred_id = pychuck.__CHUCK__.get_shred_id()
        code = _code_transform(open(filepath).read(), shred_id)
        exec(code, globals())
        return globals()[f'_chuck_shred_{shred_id}']


class _Chuck:
    def __init__(self, sample_rate: int = 22050, buffer_size: int = 64, verbose: bool = False):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.verbose = verbose

        self.stream = sd.Stream(samplerate=self.sample_rate, blocksize=self.buffer_size, channels=1, dtype='float32',
                                callback=self.callback)

        self.queue = queue.Queue()

        self.shreds = []
        self.current_shred = None
        self.shred_id = 0

        self.ready = threading.Event()
        self.ready.set()
        self.go = threading.Event()

        self.in_buffer = np.zeros(self.buffer_size, dtype='float32')
        self.out_buffer = np.zeros(self.buffer_size, dtype='float32')

        self.init_global()

    def init_global(self):
        pychuck.__CHUCK__ = self
        pychuck.now = _ChuckNow()
        pychuck.adc = _ADC()
        pychuck.dac = _DAC()
        pychuck.blackhole = _Blackhole()

    def get_shred_id(self):
        self.shred_id += 1
        return self.shred_id - 1

    def clear(self):
        pychuck.adc.clear()
        pychuck.dac.clear()
        pychuck.blackhole.clear()

    def compute(self, frames: int):
        pychuck.adc.compute(frames)
        pychuck.dac.compute(frames)
        pychuck.blackhole.compute(frames)

    def callback(self, indata, outdata, frames, time, status):
        self.ready.wait()
        self.ready.clear()
        outdata[:, 0] = self.out_buffer
        self.in_buffer[:] = indata[:, 0]
        self.go.set()

    def start(self):
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
                # print
                if self.verbose:
                    print(self.shreds[0].frames)
                    print(pychuck.dac.prev)
                # clear
                self.clear()
                # compute
                frames = min(frames_left, min(shred.frames for shred in self.shreds))
                pychuck.adc.buffer[:frames] = self.in_buffer[fi:fi + frames]
                self.compute(frames)
                self.out_buffer[fi:fi + frames] = pychuck.dac.buffer[:frames]
                # update
                for shred in self.shreds:
                    shred.update(frames)
                pychuck.now.frame += frames
                fi += frames
                frames_left -= frames
            self.ready.set()
