import numpy as np

from .util import _ChuckDur


class UGen:
    def __init__(self, gain: float = 1, op: int = 0, VM=None, *args, **kwargs):
        VM._current_shred._modules.append(self)
        self.chan = [self]
        self.gain = gain
        self.last = 0
        self.op = op
        self._sample_rate = VM._sample_rate
        self._buffer_size = VM._buffer_size
        self._in_buffer = np.zeros(self._buffer_size, dtype=np.float32)
        self._buffer = np.zeros(self._buffer_size, dtype=np.float32)
        self._computed = False
        self._in_modules = []
        self._out_modules = []

    def __setattr__(self, key, value):
        if key == 'gain':
            for chan in self.chan:
                chan.__dict__[key] = value
        super().__setattr__(key, value)

    def __ge__(self, other: 'UGen'):
        if len(self.chan) == len(other.chan):
            for i in range(len(self.chan)):
                self.chan[i]._out_modules.append(other.chan[i])
                other.chan[i]._in_modules.append(self.chan[i])
        else:
            for self_chan in self.chan:
                for other_chan in other.chan:
                    self_chan._out_modules.append(other_chan)
                    other_chan._in_modules.append(self_chan)
        return other

    def __le__(self, other: 'UGen'):
        for self_chan in self.chan:
            for other_chan in other.chan:
                if self_chan in other_chan._in_modules:
                    other_chan._in_modules.remove(self_chan)

    def _remove(self):
        for module in self._out_modules:
            if self in module._in_modules:
                module._in_modules.remove(self)
        self._out_modules.clear()
        for module in self._in_modules:
            if self in module._out_modules:
                module._out_modules.remove(self)
        self._in_modules.clear()

    def _aggreate_inputs(self, samples: int):
        if self.op == 0:
            self._in_buffer[:samples] = 0
            for module in self._in_modules:
                self._in_buffer[:samples] += module._compute_samples(samples)
        elif self.op == 3:
            self._in_buffer[:samples] = 1
            for module in self._in_modules:
                self._in_buffer[:samples] *= module._compute_samples(samples)

    def _compute_samples(self, samples: int) -> np.ndarray:
        if not self._computed:
            self._computed = True
            self._aggreate_inputs(samples)
            self._compute(samples)
            self._buffer[:samples] *= self.gain
            self.last = self._buffer[samples - 1]
        return self._buffer[:samples]

    def _compute(self, samples: int):
        for i in range(samples):
            self._buffer[i] = self._tick(self._in_buffer[i])

    def _tick(self, input: float) -> float:
        raise NotImplementedError


class _STK(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._libstk_wrapper = kwargs['VM']._libstk_wrapper
        self._stk_object = getattr(self._libstk_wrapper, f'{self.__class__.__name__}_ctor')()

    def _tick(self, input: float) -> float:
        return getattr(self._libstk_wrapper, f'{self.__class__.__name__}_tick')(self._stk_object, input)

    def __del__(self):
        getattr(self._libstk_wrapper, f'{self.__class__.__name__}_dtor')(self._stk_object)


class _Blackhole(UGen):
    def _compute_samples(self, samples: int) -> np.ndarray:
        if not self._computed:
            self._computed = True
            for module in self._in_modules:
                module._compute_samples(samples)
        return self._buffer[:samples]


class _ADCChannel(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._i = 0

    def _compute_samples(self, samples: int) -> np.ndarray:
        if not self._computed:
            self._computed = True
            self._buffer[self._i:self._i + samples] *= self.gain
            self._i = (self._i + samples) % self._buffer_size
        return self._buffer[self._i - samples:self._i or None]


class _ADC(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chan = [_ADCChannel(*args, **kwargs) for _ in range(kwargs['VM']._in_channels)]
        self.left = self.chan[0]
        self.right = self.chan[-1]

    def _set(self, indata: np.ndarray):
        for i in range(len(self.chan)):
            self.chan[i]._buffer[:] = indata[:, i]


class _DACChannel(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._i = 0

    def _compute_samples(self, samples: int) -> np.ndarray:
        if not self._computed:
            self._computed = True
            self._aggreate_inputs(samples)
            self._buffer[self._i:self._i + samples] = self._in_buffer[:samples] * self.gain
            self._i = (self._i + samples) % self._buffer_size
        return self._buffer[self._i - samples:self._i or None]


class _DAC(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chan = [_DACChannel(*args, **kwargs) for _ in range(kwargs['VM']._out_channels)]
        self.left = self.chan[0]
        self.right = self.chan[-1]

    def _compute_samples(self, samples: int) -> np.ndarray:
        for chan in self.chan:
            chan._compute_samples(samples)

    def _get(self) -> np.ndarray:
        return np.stack([chan._buffer for chan in self.chan], axis=1)


class ADC(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ADSR(_STK):
    def __init__(self, A: _ChuckDur = None, D: _ChuckDur = None, S: float = 1., R: _ChuckDur = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if all([A, D, S, R]):
            self.set(A, D, S, R)
        self.releaseTime = R.copy()

    def set(self, A: _ChuckDur, D: _ChuckDur, S: float, R: _ChuckDur):
        s = _ChuckDur(self._sample_rate)
        void = self._libstk_wrapper.ADSR_setAllTimes(
            self._stk_object, float(A / s), float(D / s), float(S), float(R / s))

    def _compute(self, samples: int):
        for i in range(samples):
            self._buffer[i] = self._tick() * self._in_buffer[i]

    def _tick(self) -> float:
        float_type = self._libstk_wrapper.ADSR_tick(self._stk_object)
        return float_type

    def keyOn(self):
        void = self._libstk_wrapper.ADSR_keyOn(self._stk_object)

    def keyOff(self):
        void = self._libstk_wrapper.ADSR_keyOff(self._stk_object)


class AI(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AutoCorr(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BandedWG(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BeeThree(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BiQuad(_STK):
    def __init__(self, prad: float = None, pfreq: float = None, eqzs: bool = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prad = prad
        self.pfreq = pfreq
        self.eqzs = eqzs

    def __setattr__(self, key, value):
        if key == 'prad':
            if value is not None and hasattr(self, 'pfreq'):
                void = self._libstk_wrapper.BiQuad_setResonance(self._stk_object, float(self.pfreq), float(value))
        elif key == 'pfreq':
            if value is not None and hasattr(self, 'prad'):
                void = self._libstk_wrapper.BiQuad_setResonance(self._stk_object, float(value), float(self.prad))
        elif key == 'eqzs':
            if value is True:
                void = self._libstk_wrapper.BiQuad_setEqualGainZeroes(self._stk_object)
        super().__setattr__(key, value)


class Blit(_STK):
    def __init__(self, harmonics: int = None, freq: float = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.harmonics = harmonics
        self.freq = freq

    def __setattr__(self, key, value):
        if key == 'harmonics':
            if value is not None:
                void = self._libstk_wrapper.Blit_setHarmonics(self._stk_object, int(value))
        elif key == 'freq':
            if value is not None:
                void = self._libstk_wrapper.Blit_setFrequency(self._stk_object, float(value))
        super().__setattr__(key, value)

    def _compute(self, samples: int):
        for i in range(samples):
            self._buffer[i] = self._tick()

    def _tick(self) -> float:
        float_type = self._libstk_wrapper.Blit_tick(self._stk_object)
        return float_type


class BlitSaw(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BlitSquare(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BlowBotl(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BlowHole(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BLT(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Bowed(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BPF(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Brass(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BRF(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Centroid(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Chorus(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Chroma(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Chugen(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Chugraph(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CKDoc(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Clarinet(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CNoise(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ConsoleInput(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CurveTable(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DAC(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DCT(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Delay(_STK):
    def __init__(self, delay: _ChuckDur = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delay = delay

    def __setattr__(self, key, value):
        if key == 'delay':
            if value is not None:
                void = self._libstk_wrapper.Delay_setDelay(self._stk_object, int(value))
        super().__setattr__(key, value)


class DelayA(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DelayL(_STK):
    def __init__(self, max: _ChuckDur = None, delay: _ChuckDur = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max = max
        self.delay = delay

    def __setattr__(self, key, value):
        if key == 'max':
            if value is not None:
                void = self._libstk_wrapper.DelayL_setMaximumDelay(self._stk_object, int(value))
        elif key == 'delay':
            if value is not None:
                void = self._libstk_wrapper.DelayL_setDelay(self._stk_object, float(value._samples / self._sample_rate))
        super().__setattr__(key, value)


class DelayP(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Dyno(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Echo(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Envelope(_STK):
    def __init__(self, duration: _ChuckDur = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duration = duration

    def __setattr__(self, key, value):
        if key == 'duration':
            if value is not None:
                void = self._libstk_wrapper.Envelope_setRate(self._stk_object, float(1 / int(value)))
        super().__setattr__(key, value)

    def _compute(self, samples: int):
        for i in range(samples):
            self._buffer[i] = self._tick() * self._in_buffer[i]

    def _tick(self) -> float:
        float_type = self._libstk_wrapper.Envelope_tick(self._stk_object)
        return float_type

    def keyOn(self):
        void = self._libstk_wrapper.Envelope_keyOn(self._stk_object)

    def keyOff(self):
        void = self._libstk_wrapper.Envelope_keyOff(self._stk_object)


class Event(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FeatureCollector(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FFT(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FileIO(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FilterBasic(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FilterStk(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Flip(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Flute(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Flux(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FM(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FMVoices(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FrencHrn(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FullRect(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Gain(UGen):
    def _compute(self, samples: int):
        self._buffer[:samples] = self._in_buffer[:samples]


class Gen10(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Gen17(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Gen5(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Gen7(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Gen9(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GenX(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HalfRect(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HevyMetl(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Hid(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HidMsg(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HMM(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HnkyTonk(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HPF(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IDCT(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IFFT(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Impulse(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next = 0

    def _compute(self, samples: int):
        self._buffer[0] = self.next
        self.next = 0


class IO(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class JCRev(_STK):
    def __init__(self, mix: float = 4.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mix = mix

    def __setattr__(self, key, value):
        if key == "mix":
            void = self._libstk_wrapper.JCRev_setEffectMix(self._stk_object, float(value))
        super().__setattr__(key, value)


class JetTabl(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class KBHit(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class KNN(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class KNN2(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class KrstlChr(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Kurtosis(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LiSa(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LiSa10(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LiSa16(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LiSa2(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LiSa4(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LiSa6(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LiSa8(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LPF(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Machine(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Mandolin(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Math(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MFCC(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MidiFileIn(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MidiIn(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MidiMsg(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MidiMsgIn(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MidiMsgOut(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MidiOut(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MidiRW(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Mix2(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MLP(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ModalBar(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Modulate(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Moog(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Noise(UGen):
    def _compute(self, samples: int):
        self._buffer[:samples] = np.random.uniform(-1, 1, samples)


class NRev(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Object(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OnePole(_STK):
    def __init__(self, pole: float = 0.5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pole = pole

    def __setattr__(self, key, value):
        if key == "pole":
            void = self._libstk_wrapper.OnePole_setPole(self._stk_object, float(value))
        super().__setattr__(key, value)


class OneZero(_STK):
    def __init__(self, zero: float = 0.5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zero = zero

    def __setattr__(self, key, value):
        if key == "zero":
            void = self._libstk_wrapper.OneZero_setZero(self._stk_object, float(value))
        super().__setattr__(key, value)


class Osc(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OscArg(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OscEvent(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OscIn(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OscMsg(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OscOut(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OscRecv(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OscSend(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Pan2Channel(UGen):
    def _compute(self, samples: int):
        self._buffer[:samples] = self._in_buffer[:samples]


class Pan2(UGen):
    def __init__(self, pan: float = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chan = [Pan2Channel(*args, **kwargs) for _ in range(2)]
        self.left = self.chan[0]
        self.right = self.chan[1]
        self.pan = pan

    def __setattr__(self, key, value):
        if key == 'pan':
            # value: (-1, 1)
            self.chan[0].gain = 1 - value
            self.chan[1].gain = 1 + value
        super().__setattr__(key, value)


class PCA(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PercFlut(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Phasor(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class pilF(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PitShift(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PoleZero(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PRCRev(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PulseOsc(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RegEx(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ResonZ(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Rhodey(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RMS(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RollOff(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SawOsc(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Saxofony(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SerialIO(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SFM(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Shakers(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Shred(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SinOsc(_STK):
    def __init__(self, freq: float = 220.0, *args, **kwargs):
        UGen.__init__(self, *args, **kwargs)
        self._libstk_wrapper = kwargs['VM']._libstk_wrapper
        self._stk_object = self._libstk_wrapper.SineWave_ctor()
        self.freq = freq

    def __setattr__(self, key, value):
        if key == 'freq':
            void = self._libstk_wrapper.SineWave_setFrequency(self._stk_object, float(value))
        super().__setattr__(key, value)

    def _tick(self, input: float) -> float:
        float_type = self._libstk_wrapper.SineWave_tick(self._stk_object)
        return float_type

    def __del__(self):
        void = self._libstk_wrapper.SineWave_dtor(self._stk_object)


class Sitar(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SndBuf(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SndBuf2(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SqrOsc(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StdErr(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StdOut(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Step(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next = 0

    def _compute(self, samples: int):
        self._buffer[:samples] = self.next


class StifKarp(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StkInstrument(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class string(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StringTokenizer(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SubNoise(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SVM(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Teabox(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TriOsc(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TubeBell(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TwoPole(_STK):
    def __init__(self, radius: float = 0.9, freq: float = 220.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius = radius
        self.freq = freq

    def __setattr__(self, key, value):
        if key == 'radius':
            if hasattr(self, 'freq'):
                void = self._libstk_wrapper.TwoPole_setResonance(self._stk_object, float(self.freq), float(value))
        elif key == 'freq':
            if hasattr(self, 'radius'):
                void = self._libstk_wrapper.TwoPole_setResonance(self._stk_object, float(value), float(self.radius))
        super().__setattr__(key, value)


class TwoZero(_STK):
    def __init__(self, b0: float = 0.0, b1: float = 0.0, b2: float = 0.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2

    def __setattr__(self, key, value):
        if key == 'b0':
            void = self._libstk_wrapper.TwoZero_setB0(self._stk_object, float(value))
        elif key == 'b1':
            void = self._libstk_wrapper.TwoZero_setB1(self._stk_object, float(value))
        elif key == 'b2':
            void = self._libstk_wrapper.TwoZero_setB2(self._stk_object, float(value))
        super().__setattr__(key, value)


class Type(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UAna(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UAnaBlob(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UGen_Multi(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UGen_Stereo(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class VoicForm(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WarpTable(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WaveLoop(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Wekinator(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Windowing(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Word2Vec(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Wurley(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WvIn(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WvOut(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WvOut2(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class XCorr(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ZeroX(UGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
