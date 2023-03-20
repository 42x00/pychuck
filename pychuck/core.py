import asyncio
import queue
import sys
import threading
import types

import numpy as np
import sounddevice as sd

import pychuck
from pychuck.module.base import _ADC, _DAC, _Blackhole
from pychuck.util import _ChuckTime, _code_transform, _ChuckDur


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
            frames = int(next(self._generator)._frames)
            if frames <= 0:
                raise ValueError("Duration must be greater than 0")
            self._frames = frames
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
                pychuck.__CHUCK__._shreds.remove(self)


class _Chuck:
    def __init__(self, sample_rate: int = 22050, buffer_size: int = 64, verbose: bool = False):
        pychuck.__CHUCK__ = self
        # options
        self._sample_rate = sample_rate
        self._buffer_size = buffer_size
        self._verbose = verbose
        # shreds
        self._queue = queue.Queue()
        self._shreds = []
        self._current_shred = _ChuckShred()
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

    def _compute_graph(self, frames: int):
        for shred in self._shreds:
            for module in shred._modules:
                module._computed = False
        pychuck.adc._computed = False
        pychuck.blackhole._compute(frames)
        pychuck.dac._compute(frames)

    async def stream_generator(self):
        q_in = asyncio.Queue()
        q_out = queue.Queue()
        loop = asyncio.get_event_loop()

        def callback(indata, outdata, frame_count, time_info, status):
            loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))
            try:
                outdata[:] = q_out.get_nowait()
            except queue.Empty:
                pass

        stream = sd.Stream(samplerate=self._sample_rate, blocksize=self._buffer_size, dtype=np.float32,
                           callback=callback)
        with stream:
            while True:
                indata, status = await q_in.get()
                outdata = np.empty((self._buffer_size, 1), dtype=np.float32)
                yield indata, outdata, status
                q_out.put_nowait(outdata)

    async def _main(self):
        async for indata, outdata, status in self.stream_generator():
            if status:
                print(status)

            pychuck.adc.buffer[:] = indata[:, 0]
            pychuck.adc._i = pychuck.dac._i = 0

            frames_left = outdata.shape[0]
            while frames_left > 0:
                # add shreds
                while not self._queue.empty():
                    _ChuckShred(self._queue.get())
                # compute
                frames = self._get_min_shred_frames(frames_left)
                self._compute_graph(frames)
                # update
                pychuck.now._frame += frames
                frames_left -= frames
                for shred in self._shreds:
                    shred._update(frames)

            outdata[:, 0] = pychuck.dac.buffer

    async def _run(self):
        asyncio.create_task(self._main())
        await asyncio.sleep(1e10)

    def start(self):
        print(f'Chuck:\n    sample_rate: {self._sample_rate}\n    buffer_size: {self._buffer_size}')
        try:
            asyncio.run(self._run())
        except KeyboardInterrupt:
            sys.exit('\nInterrupted by user')

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
