from typing import List

import numpy as np
import pychuck


class _Unit:
    def __init__(self, add_to_shred: bool = True, add_to_graph: bool = True):
        if add_to_shred:
            pychuck.me._units.append(self)
        if add_to_graph:
            pychuck.VM._graph.add_node(self)
        self.chan: List[_Unit] = [self]

    def __rshift__(self, other: '_Unit') -> '_Unit':
        if len(self.chan) == len(other.chan):
            for self_chan, other_chan in zip(self.chan, other.chan):
                pychuck.VM._graph.add_edge(self_chan, other_chan)
        else:
            for self_chan in self.chan:
                for other_chan in other.chan:
                    pychuck.VM._graph.add_edge(self_chan, other_chan)
        pychuck.VM._sort_graph()
        return other

    def __lshift__(self, other: '_Unit'):
        for self_chan in self.chan:
            for other_chan in other.chan:
                pychuck.VM._graph.remove_edge(self_chan, other_chan)
        pychuck.VM._sort_graph()

    def _remove(self):
        pychuck.VM._graph.remove_node(self)
        pychuck.VM._sort_graph()

    def _compute(self, samples: int):
        raise NotImplementedError


class UGen(_Unit):
    def __init__(self, gain: float = 1.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gain: float = gain
        self.buffered: np.ndarray
        self._buffer: np.ndarray = np.zeros(pychuck.VM._buffer_size, dtype=np.float32)
        self._in_buffer: np.ndarray = np.zeros_like(self._buffer)

    def _compute(self, samples: int):
        self._aggregate_input(samples)
        self.buffered = self._tick(samples) * self.gain

    def _aggregate_input(self, samples: int):
        self._in_buffer.fill(0)
        for predecessor in pychuck.VM._graph.predecessors(self):
            self._in_buffer[:samples] += predecessor.buffered

    def _tick(self, samples: int) -> np.ndarray:
        raise NotImplementedError


class _ADCChannel(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(add_to_shred=False, *args, **kwargs)
        self._i = 0

    def _compute(self, samples: int):
        self.buffered = self._buffer[self._i:self._i + samples] * self.gain
        self._i += samples


class _ADC(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(add_to_shred=False, add_to_graph=False, *args, **kwargs)
        self.chan = [_ADCChannel(*args, **kwargs) for _ in range(pychuck.VM._in_channels)]

    def _set_buffer(self, indata: np.ndarray):
        length = len(indata)
        for i, chan in enumerate(self.chan):
            chan._buffer[:length] = indata[:, i]
            chan._i = 0


class _DACChannel(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(add_to_shred=False, *args, **kwargs)
        self._i = 0

    def _compute(self, samples: int):
        self._aggregate_input(samples)
        self.buffered = self._in_buffer[:samples] * self.gain
        self._buffer[self._i:self._i + samples] = self.buffered
        self._i += samples


class _DAC(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(add_to_shred=False, add_to_graph=False, *args, **kwargs)
        self.chan = [_DACChannel(*args, **kwargs) for _ in range(pychuck.VM._out_channels)]

    def _get_buffer(self, length: int) -> np.ndarray:
        for chan in self.chan:
            chan._i = 0
        return np.stack([chan._buffer[:length] for chan in self.chan], axis=1)


class _Blackhole(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(add_to_shred=False, *args, **kwargs)

    def _compute(self, samples: int):
        pass


class SinOsc(UGen):
    def __init__(self, freq: float = 440.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.freq: float = freq
        self._phase: float = -np.pi / 2
        self._sample_rate: int = pychuck.VM._sample_rate

    def _compute(self, samples: int):
        new_phase = self._phase + samples * 2 * np.pi * self.freq / self._sample_rate
        self.buffered = np.sin(np.linspace(self._phase, new_phase, samples, endpoint=False)) * self.gain
        self._phase = new_phase
