import numpy as np
import pychuck


class _Unit:
    def __init__(self, _add2me: bool = True, *args, **kwargs):
        if _add2me:
            pychuck.me._units.append(self)
        pychuck.VM._graph.add_node(self)

    def __rshift__(self, other: '_Unit') -> '_Unit':
        pychuck.VM._graph.add_edge(self, other)
        pychuck.VM._update_graph()
        return other

    def __lshift__(self, other: '_Unit'):
        pychuck.VM._graph.remove_edge(self, other)
        pychuck.VM._update_graph()

    def _remove(self):
        pychuck.VM._graph.remove_node(self)
        pychuck.VM._update_graph()

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
        self._in_buffer.fill(0.0)
        for pred in pychuck.VM._graph.predecessors(self):
            self._in_buffer[:samples] += pred.buffered

    def _tick(self, samples: int) -> np.ndarray:
        raise NotImplementedError


class _ADC(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._i = 0

    def _compute(self, samples: int):
        self.buffered = self._in_buffer[self._i:self._i + samples] * self.gain
        self._i += samples

    def _set_buffer(self, indata: np.ndarray):
        length = len(indata)
        self._in_buffer[:length] = indata
        self._i = 0


class _DAC(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._i = 0

    def _compute(self, samples: int):
        self._aggregate_input(samples)
        self.buffered = self._in_buffer[:samples] * self.gain
        self._buffer[self._i:self._i + samples] = self.buffered
        self._i += samples

    def _get_buffer(self, length: int) -> np.ndarray:
        self._i = 0
        return self._buffer[:length]


class _Blackhole(UGen):
    def _compute(self, samples: int):
        pass


class Gain(UGen):
    def _tick(self, samples: int) -> np.ndarray:
        return self._in_buffer[:samples]


class SinOsc(UGen):
    def __init__(self, freq: float = 440.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.freq: float = freq
        self._phase: float = -np.pi / 2
        self._sample_rate: int = pychuck.VM._sample_rate

    def _tick(self, samples: int) -> np.ndarray:
        phase = self._phase + samples * 2 * np.pi * self.freq / self._sample_rate
        ret = np.sin(np.linspace(self._phase, phase, samples, endpoint=False))
        self._phase = phase
        return ret
