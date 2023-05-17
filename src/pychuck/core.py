import argparse
import queue
from types import GeneratorType
from typing import List

import networkx as nx
import numpy as np
import pychuck
from .unit import _Unit
from .util import _wrap_code, _init_globals


class _Shred:
    def __init__(self, generator: GeneratorType):
        self._samples_left: int = 0
        self._units: List[_Unit] = []
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
        for unit in self._units:
            unit._remove()
        pychuck.VM._shreds.remove(self)


class _Chuck:
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 256):
        pychuck.VM = self
        self._sample_rate: int = sample_rate
        self._buffer_size: int = buffer_size
        self._units: List[_Unit] = []
        self._shreds: List[_Shred] = []
        self._event_queue = queue.Queue()
        self._graph = nx.DiGraph()
        _init_globals(sample_rate)

    def callback(self, in_data: np.ndarray) -> np.ndarray:
        pychuck.adc._set_buffer(in_data)

        while not self._event_queue.empty():
            self._handle_event(self._event_queue.get())

        samples_left = length = len(in_data)
        while samples_left > 0:
            samples_to_compute = min([samples_left] + [shred._samples_left for shred in self._shreds])
            self._compute(samples_to_compute)
            self._update_shreds(samples_to_compute)
            samples_left -= samples_to_compute

        return pychuck.dac._get_buffer(length)

    def add_shred(self, code: str):
        exec(_wrap_code(code), globals())
        self._event_queue.put(globals()['__shred__']())

    def start(self):
        import pyaudio
        import time
        def callback(in_data, frame_count, time_info, status_flags):
            in_data = np.frombuffer(in_data, dtype=np.float32)
            out_data = self.callback(in_data).tobytes()
            return (out_data, pyaudio.paContinue)

        pyaudio.PyAudio().open(rate=self._sample_rate,
                               channels=1,
                               format=pyaudio.paFloat32,
                               input=True,
                               output=True,
                               frames_per_buffer=self._buffer_size,
                               stream_callback=callback)
        time.sleep(1e5)

    def _handle_event(self, event):
        _Shred(event)

    def _compute(self, samples: int):
        for unit in self._units:
            unit._compute(samples)

    def _update_shreds(self, samples: int):
        for shred in self._shreds:
            shred._samples_left -= samples
            if shred._samples_left <= 0:
                shred._next()

    def _update_graph(self):
        try:
            self._units = list(nx.topological_sort(self._graph))
        except nx.NetworkXUnfeasible:
            raise RuntimeError('Cyclic dependency detected')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--srate', type=int, default=44100)
    parser.add_argument('--bufsize', type=int, default=256)
    parser.add_argument('files', nargs='+', type=str)
    args = parser.parse_args()
    chuck = _Chuck(sample_rate=args.srate, buffer_size=args.bufsize)
    for file in args.files:
        chuck.add_shred(open(file).read())
    chuck.start()
