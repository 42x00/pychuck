import numpy as np

import pychuck


class UGen:
    def __init__(self):
        pychuck.__CHUCK__._current_shred._modules.append(self)
        self._in_modules = []
        self._out_modules = []
        self._chuck_buffer_size = pychuck.__CHUCK__._buffer_size
        self._in_buffer = np.zeros(self._chuck_buffer_size)
        self._buffer = np.zeros(self._chuck_buffer_size)
        self._computed = False

    def __rshift__(self, other: 'UGen'):
        self._out_modules.append(other)
        other._in_modules.append(self)
        return other

    def __lshift__(self, other: 'UGen'):
        if self in other._in_modules:
            other._in_modules.remove(self)

    def _remove(self):
        for module in self._out_modules:
            module._in_modules.remove(self)
        for module in self._in_modules:
            module._out_modules.remove(self)

    def _aggregate_inputs(self, samples: int):
        self._in_buffer[:samples] = 0
        for module in self._in_modules:
            self._in_buffer[:samples] += module._compute_samples(samples)

    def _compute_samples(self, samples: int):
        if not self._computed:
            self._computed = True
            self._aggregate_inputs(samples)
            self._buffer[:samples] = self._compute(self._in_buffer[:samples])
        return self._buffer[:samples]

    def _compute(self, indata: np.ndarray):
        raise NotImplementedError


class _ADC(UGen):
    def __init__(self):
        super().__init__()
        self._i = 0

    def _compute_samples(self, samples: int):
        if not self._computed:
            self._computed = True
            self._i += samples
            self._i %= self._chuck_buffer_size
        return self._buffer[self._i - samples:self._i or None]


class _DAC(UGen):
    def __init__(self):
        super().__init__()
        self._i = 0

    def _compute_samples(self, samples: int):
        if not self._computed:
            self._computed = True
            self._aggregate_inputs(samples)
            self._buffer[self._i:self._i + samples] = self._in_buffer[:samples]
            self._i += samples
            self._i %= self._chuck_buffer_size
        return self._buffer[self._i - samples:self._i or None]


class _Blackhole(UGen):
    def _compute_samples(self, samples: int):
        if not self._computed:
            self._computed = True
            for module in self._in_modules:
                module._compute_samples(samples)

class Gain(UGen):
    pass

class Noise(UGen):
    pass

class Impulse(UGen):
    pass

class Step(UGen):
    pass

class Halfrect(UGen):
    pass


class Fullrect(UGen):
    pass


class Zerox(UGen):
    pass


class Biquad(UGen):
    pass


class Filter(UGen):
    pass


class Onepole(UGen):
    pass


class Twopole(UGen):
    pass


class Onezero(UGen):
    pass


class Twozero(UGen):
    pass


class Polezero(UGen):
    pass


class Lpf(UGen):
    pass


class Hpf(UGen):
    pass


class Bpf(UGen):
    pass


class Brf(UGen):
    pass


class Resonz(UGen):
    pass


class Filterbasic(UGen):
    pass


class Dyno(UGen):
    pass


class Delayp(UGen):
    pass


class Sndbuf(UGen):
    pass


class Phasor(UGen):
    pass


class SinOsc(UGen):
    pass


class PulseOsc(UGen):
    pass


class SqrOsc(UGen):
    pass


class TriOsc(UGen):
    pass


class SawOsc(UGen):
    pass


class Genx(UGen):
    pass


class Gen5(UGen):
    pass


class Gen7(UGen):
    pass


class Gen9(UGen):
    pass


class Gen10(UGen):
    pass


class Gen17(UGen):
    pass


class Curvetable(UGen):
    pass


class Lisa(UGen):
    pass


class Netout(UGen):
    pass


class Netin(UGen):
    pass


class Pan2(UGen):
    pass


class Mix2(UGen):
    pass


class Stkinstrument(UGen):
    pass


class Bandedwg(UGen):
    pass


class Blowbotl(UGen):
    pass


class Blowhole(UGen):
    pass


class Bowed(UGen):
    pass


class Brass(UGen):
    pass


class Clarinet(UGen):
    pass


class Flute(UGen):
    pass


class Mandolin(UGen):
    pass


class Modalbar(UGen):
    pass


class Moog(UGen):
    pass


class Saxofony(UGen):
    pass


class Shakers(UGen):
    pass


class Sitar(UGen):
    pass


class Stifkarp(UGen):
    pass


class Voicform(UGen):
    pass


class Fm(UGen):
    pass


class Beethree(UGen):
    pass


class Fmvoices(UGen):
    pass


class Hevymetl(UGen):
    pass


class Percflut(UGen):
    pass


class Rhodey(UGen):
    pass


class Tubebell(UGen):
    pass


class Wurley(UGen):
    pass


class Delay(UGen):
    pass


class Delaya(UGen):
    pass


class Delayl(UGen):
    pass


class Echo(UGen):
    pass


class Envelope(UGen):
    pass


class Adsr(UGen):
    pass


class Jcrev(UGen):
    pass


class Nrev(UGen):
    pass


class Prcrev(UGen):
    pass


class Chorus(UGen):
    pass


class Modulate(UGen):
    pass


class Pitshift(UGen):
    pass


class Subnoise(UGen):
    pass


class Blit(UGen):
    pass


class Blitsaw(UGen):
    pass


class Blitsquare(UGen):
    pass


class Wvin(UGen):
    pass


class Waveloop(UGen):
    pass


class Wvout(UGen):
    pass
