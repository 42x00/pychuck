import argparse
import queue
from types import GeneratorType
from typing import List

import sounddevice as sd
import networkx as nx
import numpy as np
import pychuck
from .unit import _Unit
from .util import _wrap_code, _init_globals


class _Shred:
    def __init__(self, generator: GeneratorType):
        self._samples_left: int = 0
        self._units: List[_Unit] = []
        self._shreds: List[_Shred] = []
        self._generator: GeneratorType = generator
        if self._next():
            pychuck.VM._shreds.append(self)

    def _next(self):
        pychuck.me = self
        try:
            self._samples_left = int(next(self._generator))
            if self._samples_left < 0:
                raise ValueError('Duration must be positive')
            return True
        except StopIteration:
            self._remove()
        return False

    def _remove(self):
        for shred in self._shreds:
            shred._remove()
        self._shreds.clear()
        for unit in self._units:
            unit._remove()
        self._units.clear()
        pychuck.VM._shreds.remove(self)


class _Chuck:
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 256, in_channels: int = 1, out_channels: int = 2):
        pychuck.VM = self
        self._sample_rate: int = sample_rate
        self._buffer_size: int = buffer_size
        self._in_channels: int = in_channels
        self._out_channels: int = out_channels
        self._shreds: List[_Shred] = []
        self._event_queue = queue.Queue()
        self._graph = nx.DiGraph()
        self._sorted_graph: List[_Unit] = []
        _init_globals(sample_rate)

    def callback(self, indata: np.ndarray) -> np.ndarray:
        pychuck.adc._set_buffer(indata)

        while not self._event_queue.empty():
            self._handle_event(self._event_queue.get())

        samples_left = length = len(indata)
        while samples_left > 0:
            samples_to_compute = min([samples_left] + [shred._samples_left for shred in self._shreds])

            for unit in self._sorted_graph:
                unit._compute(samples_to_compute)

            pychuck.now._value += samples_to_compute
            for shred in self._shreds:
                shred._samples_left -= samples_to_compute
                if shred._samples_left <= 0:
                    shred._next()

            samples_left -= samples_to_compute

        return pychuck.dac._get_buffer(length)

    def add_shred(self, code: str):
        exec(_wrap_code(code), globals())
        self._event_queue.put(globals()['__shred__']())

    def start(self):
        def callback(indata, outdata, frames, time, status):
            if status:
                print(status)
            outdata[:] = self.callback(indata)

        sd.Stream(samplerate=self._sample_rate, blocksize=self._buffer_size,
                  channels=(self._in_channels, self._out_channels), dtype=np.float32,
                  callback=callback).start()
        try:
            sd.sleep(1000000)
        except KeyboardInterrupt:
            pass

    def _handle_event(self, event):
        # TODO: Handle more events
        _Shred(event)

    def _sort_graph(self):
        # TODO: Check for cycles
        self._sorted_graph = list(nx.topological_sort(self._graph))


def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--srate', type=int, default=44100)
    parser.add_argument('--bufsize', type=int, default=256)
    parser.add_argument('--in', type=int, default=1, dest='in_channels')
    parser.add_argument('--out', type=int, default=2)
    parser.add_argument('files', nargs='+', type=str)
    args = parser.parse_args()
    chuck = _Chuck(sample_rate=args.srate, buffer_size=args.bufsize,
                   in_channels=args.in_channels, out_channels=args.out)
    for file in args.files:
        chuck.add_shred(open(file).read())
    chuck.start()
