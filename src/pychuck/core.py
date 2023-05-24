import argparse
import queue
from types import GeneratorType
from typing import List

import sounddevice as sd
import networkx as nx
import numpy as np
import pychuck
from .unit import _Unit
from .util import _wrap_code, _init_globals, _Event


class _Shred:
    def __init__(self, generator: GeneratorType, name: str = 'Untitled'):
        self._id = pychuck.VM._shred_id
        pychuck.VM._shred_id += 1
        self._name: str = name
        self._samples_left: int = 0
        self._samples_computed: int = 0
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
            pass
        except Exception as e:
            print(e)
        self._remove()
        return False

    def _remove(self):
        for shred in self._shreds:
            shred._remove()
        self._shreds.clear()
        for unit in self._units:
            unit._remove()
        self._units.clear()
        if self in pychuck.VM._shreds:
            pychuck.VM._shreds.remove(self)


class _Chuck:
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 256, in_channels: int = 1, out_channels: int = 2):
        pychuck.VM = self
        self._sample_rate: int = sample_rate
        self._buffer_size: int = buffer_size
        self._in_channels: int = in_channels
        self._out_channels: int = out_channels
        self._shred_id: int = 0
        self._shreds: List[_Shred] = []
        self._event_queue = queue.Queue()
        self._graph = nx.DiGraph()
        self._sorted_graph: List[_Unit] = []
        self._stream: sd.Stream = self._init_stream()
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

            self._update_shreds(samples_to_compute)

            samples_left -= samples_to_compute

        return pychuck.dac._get_buffer(length)

    def start(self):
        self._stream.start()

    def stop(self):
        self._stream.stop()

    def add_shred(self, code: str, name: str = 'Untitled'):
        try:
            exec(_wrap_code(code), globals())
            self._event_queue.put((_Event.ADD_SHRED, globals()['__shred__'](), name))
        except Exception as e:
            print(e)

    def replace_shred(self, code: str, name: str = 'Untitled'):
        self.remove_shred(name)
        self.add_shred(code, name)

    def remove_shred(self, name: str = None, id: int = None):
        self._event_queue.put((_Event.REMOVE_SHRED, name, id))

    def remove_last_shred(self):
        self._event_queue.put((_Event.REMOVE_LAST_SHRED,))

    def clear_vm(self):
        self._event_queue.put((_Event.CLEAR_VM,))

    def _handle_event(self, event):
        if event[0] == _Event.ADD_SHRED:
            _Shred(event[1], event[2])
        elif event[0] == _Event.REMOVE_SHRED:
            if event[2] is not None:
                for shred in self._shreds:
                    if shred._id == event[2]:
                        shred._remove()
                        break
            else:
                for shred in self._shreds:
                    if shred._name == event[1]:
                        shred._remove()
                        break
        elif event[0] == _Event.REMOVE_LAST_SHRED:
            if len(self._shreds) > 0:
                self._shreds[-1]._remove()
        elif event[0] == _Event.CLEAR_VM:
            while len(self._shreds) > 0:
                self._shreds[0]._remove()

    def _init_stream(self):
        def callback(indata, outdata, frames, time, status):
            outdata[:] = self.callback(indata)

        return sd.Stream(samplerate=self._sample_rate, blocksize=self._buffer_size,
                         channels=(self._in_channels, self._out_channels), dtype=np.float32,
                         callback=callback)

    def _sort_graph(self):
        # TODO: Check for cycles
        self._sorted_graph = list(nx.topological_sort(self._graph))

    def _update_shreds(self, samples: int):
        pychuck.now._value += samples
        for shred in self._shreds:
            shred._samples_left -= samples
            shred._samples_computed += samples
        while len(self._shreds) > 0:
            flag = True
            for shred in self._shreds:
                if shred._samples_left <= 0:
                    shred._next()
                    flag = False
                    break
            if flag:
                break


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
    try:
        sd.sleep(1000000)
    except KeyboardInterrupt:
        pass


def main_gui():
    import sys
    from PyQt6 import QtWidgets
    from .gui import MainWindow
    _Chuck()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
