import ctypes

import numpy as np

import pychuck
from pychuck.util import _ChuckDur

libstk_wrapper = ctypes.CDLL('/Users/ykli/research/pychuck/workspace/wrapper/libstk_wrapper.so')


class UGen:
    def __init__(self):
        pychuck.__CHUCK__._current_shred._modules.append(self)
        self.gain = 1
        self.last = 0
        self._in_modules = []
        self._out_modules = []
        self._chuck_sample_rate = pychuck.__CHUCK__._sample_rate
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
            self._out_modules.remove(other)

    def _remove(self):
        for module in self._out_modules:
            module._in_modules.remove(self)
        for module in self._in_modules:
            module._out_modules.remove(self)

    def _aggregate_inputs(self, samples: int):
        self._in_buffer.fill(0)
        for module in self._in_modules:
            self._in_buffer[:samples] += module._compute_samples(samples)

    def _compute_samples(self, samples: int):
        if not self._computed:
            self._computed = True
            self._aggregate_inputs(samples)
            for i in range(samples):
                self._buffer[i] = self._tick(i)
            self._buffer[:samples] *= self.gain
            self.last = self._buffer[samples - 1]
        return self._buffer[:samples]

    def _tick(self, index: int):
        raise NotImplementedError


class _ADC(UGen):
    def __init__(self):
        super().__init__()
        self._i = 0

    def _compute_samples(self, samples: int):
        if not self._computed:
            self._computed = True
            self._buffer[self._i:self._i + samples] *= self.gain
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
            self._buffer[self._i:self._i + samples] = self._in_buffer[:samples] * self.gain
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
    def __init__(self, gain: float = 1.0):
        super().__init__()
        self.gain = gain

    def _tick(self, index: int):
        return self._in_buffer[index]


class Noise(UGen):
    def _tick(self, index: int):
        return np.random.uniform(-1, 1)


class Impulse(UGen):
    def __init__(self, gain: float = 1.0):
        super().__init__()
        self.next = 0
        self.gain = gain

    def _tick(self, index: int):
        ret = self.next
        self.next = 0
        return ret


class Step(UGen):
    pass


class Halfrect(UGen):
    pass


class Fullrect(UGen):
    pass


class Zerox(UGen):
    pass


libstk_wrapper.BiQuad_ctor.restype = ctypes.c_void_p
libstk_wrapper.BiQuad_setResonance.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double]
libstk_wrapper.BiQuad_setEqualGainZeroes.argtypes = [ctypes.c_void_p]
libstk_wrapper.BiQuad_tick.argtypes = [ctypes.c_void_p, ctypes.c_double]
libstk_wrapper.BiQuad_tick.restype = ctypes.c_double
libstk_wrapper.BiQuad_dtor.argtypes = [ctypes.c_void_p]


class BiQuad(UGen):
    def __init__(self, pfreq: float = 0, prad: float = 0, eqzs: float = 0, gain: float = 1):
        super().__init__()
        self._obj = libstk_wrapper.BiQuad_ctor()
        self.pfreq = pfreq
        self.prad = prad
        self.eqzs = eqzs
        self.gain = gain

    def __setattr__(self, key, value):
        if key == 'pfreq' or key == 'prad':
            if hasattr(self, 'pfreq') and hasattr(self, 'prad'):
                libstk_wrapper.BiQuad_setResonance(self._obj, self.pfreq, self.prad)
        elif key == 'eqzs':
            if value:
                libstk_wrapper.BiQuad_setEqualGainZeroes(self._obj)
        super().__setattr__(key, value)

    def _tick(self, index: int):
        return libstk_wrapper.BiQuad_tick(self._obj, self._in_buffer[index])

    def __del__(self):
        libstk_wrapper.BiQuad_dtor(self._obj)


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


libstk_wrapper.SineWave_ctor.restype = ctypes.c_void_p
libstk_wrapper.SineWave_setRate.argtypes = [ctypes.c_void_p, ctypes.c_double]
libstk_wrapper.SineWave_setFrequency.argtypes = [ctypes.c_void_p, ctypes.c_double]
libstk_wrapper.SineWave_tick.argtypes = [ctypes.c_void_p]
libstk_wrapper.SineWave_tick.restype = ctypes.c_double
libstk_wrapper.SineWave_dtor.argtypes = [ctypes.c_void_p]


class SinOsc(UGen):
    """
    Sine wave oscillator.

    ...

    Attributes
    ----------
    freq : float
        Frequency of the oscillator in Hz.
    gain : float
        Gain of the oscillator.
    """

    def __init__(self, freq: float = 220.0, gain: float = 1.0):
        super().__init__()
        self._obj = libstk_wrapper.SineWave_ctor()
        libstk_wrapper.SineWave_setRate(self._obj, self._chuck_sample_rate)
        self.freq = freq
        self.gain = gain

    def __setattr__(self, key, value):
        if key == 'freq':
            libstk_wrapper.SineWave_setFrequency(self._obj, value)
        super().__setattr__(key, value)

    def _tick(self, index: int):
        return libstk_wrapper.SineWave_tick(self._obj)

    def __del__(self):
        libstk_wrapper.SineWave_dtor(self._obj)


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


libstk_wrapper.Delay_ctor.restype = ctypes.c_void_p
libstk_wrapper.Delay_setDelay.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
libstk_wrapper.Delay_tick.argtypes = [ctypes.c_void_p, ctypes.c_double]
libstk_wrapper.Delay_tick.restype = ctypes.c_double
libstk_wrapper.Delay_dtor.argtypes = [ctypes.c_void_p]


class Delay(UGen):
    def __init__(self, delay: _ChuckDur = None, gain: float = 1.0):
        super().__init__()
        self._obj = libstk_wrapper.Delay_ctor()
        self.delay = delay
        self.gain = gain

    def __setattr__(self, key, value):
        if key == 'delay':
            if value is not None:
                libstk_wrapper.Delay_setDelay(self._obj, int(value._samples))
        super().__setattr__(key, value)

    def _tick(self, index: int):
        return libstk_wrapper.Delay_tick(self._obj, self._in_buffer[index])

    def __del__(self):
        libstk_wrapper.Delay_dtor(self._obj)


class Delaya(UGen):
    pass


libstk_wrapper.DelayL_ctor.restype = ctypes.c_void_p
libstk_wrapper.DelayL_setMaximumDelay.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
libstk_wrapper.DelayL_setDelay.argtypes = [ctypes.c_void_p, ctypes.c_double]
libstk_wrapper.DelayL_tick.argtypes = [ctypes.c_void_p, ctypes.c_double]
libstk_wrapper.DelayL_tick.restype = ctypes.c_double
libstk_wrapper.DelayL_dtor.argtypes = [ctypes.c_void_p]


class DelayL(UGen):
    def __init__(self, max: _ChuckDur = None, delay: _ChuckDur = None, gain: float = 1.0):
        super().__init__()
        self._obj = libstk_wrapper.DelayL_ctor()
        self.max = max
        self.delay = delay
        self.gain = gain

    def __setattr__(self, key, value):
        if key == 'max':
            if value is not None:
                libstk_wrapper.DelayL_setMaximumDelay(self._obj, int(value._samples))
        elif key == 'delay':
            if value is not None:
                libstk_wrapper.DelayL_setDelay(self._obj, value / pychuck.second)
        super().__setattr__(key, value)

    def _tick(self, index: int):
        return libstk_wrapper.DelayL_tick(self._obj, self._in_buffer[index])

    def __del__(self):
        libstk_wrapper.DelayL_dtor(self._obj)


class Echo(UGen):
    pass


libstk_wrapper.Envelope_ctor.restype = ctypes.c_void_p
libstk_wrapper.Envelope_setRate.argtypes = [ctypes.c_void_p, ctypes.c_double]
libstk_wrapper.Envelope_keyOn.argtypes = [ctypes.c_void_p]
libstk_wrapper.Envelope_keyOff.argtypes = [ctypes.c_void_p]
libstk_wrapper.Envelope_tick.argtypes = [ctypes.c_void_p]
libstk_wrapper.Envelope_tick.restype = ctypes.c_double
libstk_wrapper.Envelope_dtor.argtypes = [ctypes.c_void_p]


class Envelope(UGen):
    def __init__(self, duration: _ChuckDur = None):
        super().__init__()
        self._obj = libstk_wrapper.Envelope_ctor()
        self.duration = duration

    def __setattr__(self, key, value):
        if key == 'duration':
            if value is not None:
                libstk_wrapper.Envelope_setRate(self._obj, 1.0 / value._samples)
        super().__setattr__(key, value)

    def keyOn(self):
        libstk_wrapper.Envelope_keyOn(self._obj)

    def keyOff(self):
        libstk_wrapper.Envelope_keyOff(self._obj)

    def _tick(self, index: int):
        return libstk_wrapper.Envelope_tick(self._obj) * self._in_buffer[index]

    def __del__(self):
        libstk_wrapper.Envelope_dtor(self._obj)


libstk_wrapper.ADSR_ctor.restype = ctypes.c_void_p
libstk_wrapper.ADSR_setAllTimes.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                            ctypes.c_double]
libstk_wrapper.ADSR_keyOn.argtypes = [ctypes.c_void_p]
libstk_wrapper.ADSR_keyOff.argtypes = [ctypes.c_void_p]
libstk_wrapper.ADSR_tick.argtypes = [ctypes.c_void_p]
libstk_wrapper.ADSR_tick.restype = ctypes.c_double
libstk_wrapper.ADSR_dtor.argtypes = [ctypes.c_void_p]


class ADSR(UGen):
    def __init__(self, A: _ChuckDur = None, D: _ChuckDur = None, S: float = None, R: _ChuckDur = None):
        super().__init__()
        self.releaseTime = None
        self._obj = libstk_wrapper.ADSR_ctor()
        if all([A, D, S, R]):
            self.set(A, D, S, R)

    def set(self, A: _ChuckDur, D: _ChuckDur, S: float, R: _ChuckDur):
        self.releaseTime = R
        sec = pychuck.second
        libstk_wrapper.ADSR_setAllTimes(self._obj, A / sec, D / sec, S, R / sec)

    def keyOn(self):
        libstk_wrapper.ADSR_keyOn(self._obj)

    def keyOff(self):
        libstk_wrapper.ADSR_keyOff(self._obj)

    def _tick(self, index: int):
        return libstk_wrapper.ADSR_tick(self._obj) * self._in_buffer[index]

    def __del__(self):
        libstk_wrapper.ADSR_dtor(self._obj)


libstk_wrapper.JCRev_ctor.restype = ctypes.c_void_p
libstk_wrapper.JCRev_setEffectMix.argtypes = [ctypes.c_void_p, ctypes.c_double]
libstk_wrapper.JCRev_tick.argtypes = [ctypes.c_void_p, ctypes.c_double]
libstk_wrapper.JCRev_tick.restype = ctypes.c_double
libstk_wrapper.JCRev_dtor.argtypes = [ctypes.c_void_p]


class JCRev(UGen):
    def __init__(self, mix: float = 0.0, gain: float = 1.0):
        super().__init__()
        self._obj = libstk_wrapper.JCRev_ctor()
        self.mix = mix
        self.gain = gain

    def __setattr__(self, key, value):
        if key == 'mix':
            libstk_wrapper.JCRev_setEffectMix(self._obj, value)
        super().__setattr__(key, value)

    def _tick(self, index: int):
        return libstk_wrapper.JCRev_tick(self._obj, self._in_buffer[index])

    def __del__(self):
        libstk_wrapper.JCRev_dtor(self._obj)


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


libstk_wrapper.Blit_ctor.restype = ctypes.c_void_p
libstk_wrapper.Blit_setFrequency.argtypes = [ctypes.c_void_p, ctypes.c_double]
libstk_wrapper.Blit_setHarmonics.argtypes = [ctypes.c_void_p, ctypes.c_int]
libstk_wrapper.Blit_tick.argtypes = [ctypes.c_void_p]
libstk_wrapper.Blit_tick.restype = ctypes.c_double
libstk_wrapper.Blit_dtor.argtypes = [ctypes.c_void_p]


class Blit(UGen):
    """
    Blit is a band-limited impulse train generator.

    ...

    Attributes
    ----------
    freq : float
        Frequency of the impulse train in Hz.
    harmonics : int
        Number of harmonics to use in the synthesis of the impulse train.
    gain : float
        Overall output gain.
    """

    def __init__(self, freq: float = 220.0, harmonics: int = 100, gain: float = 1.0):
        super().__init__()
        self._obj = libstk_wrapper.Blit_ctor()
        self.freq = freq
        self.harmonics = harmonics
        self.gain = gain

    def __setattr__(self, key, value):
        if key == 'freq':
            libstk_wrapper.Blit_setFrequency(self._obj, value)
        elif key == 'harmonics':
            libstk_wrapper.Blit_setHarmonics(self._obj, value)
        super().__setattr__(key, value)

    def _tick(self, index: int):
        return libstk_wrapper.Blit_tick(self._obj)

    def __del__(self):
        libstk_wrapper.Blit_dtor(self._obj)


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
