import time
import librosa
import threading
from enum import Enum
import numpy as np
import sounddevice as sd

# ======================================================================
# Global
# ======================================================================
__CHUCK__ = None
now = None
adc = None
dac = None
blackhole = None


# ======================================================================
# Time
# ======================================================================
class _ChuckNow:
    def __init__(self):
        self.sample_count = 0

    def reset(self):
        self.sample_count = 0


class _ChuckTimeUnit(Enum):
    ms = 1e-3
    s = 1
    m = 60
    h = 3600


class Dur:
    def __init__(self, value: float, unit: str = 's'):
        global __CHUCK__
        self.value = value * __CHUCK__.sample_rate
        if unit == 'samp':
            self.value = value
        elif unit in _ChuckTimeUnit.__members__:
            self.value *= _ChuckTimeUnit[unit].value
        else:
            raise ValueError(f'Invalid time unit: {unit}')

    def __rshift__(self, other: _ChuckNow):
        sample_request = int(round(self.value))
        if sample_request > 0:
            threading.current_thread().instance.wait(sample_request)


# ======================================================================
# Chuck Module
# ======================================================================
class _ChuckModuleType(Enum):
    IN = 0  # dac, blackhole, etc.
    OUT = 1  # adc, SinOsc, etc.
    IN_OUT = 2  # FFT, etc.


class _ChuckModule:
    def __init__(self):
        self.type = None
        self.sample_rate = __CHUCK__.sample_rate
        self.buffer_size = __CHUCK__.buffer_size
        # self.prev = []
        # self.next = []

    def __rshift__(self, other: '_ChuckModule') -> '_ChuckModule':
        if self.type == _ChuckModuleType.IN:
            raise Exception(f'{self.__class__.__name__} cannot be used as an input')
        elif other.type == _ChuckModuleType.OUT:
            raise Exception(f'{other.__class__.__name__} cannot be used as an output')
        else:
            return self.connect(other)

    def append(self, other: '_ChuckModule', which: str):
        self.__dict__[which].append(other)

    def connect(self, other: '_ChuckModule') -> '_ChuckModule':
        self.append(other, 'next')
        other.append(self, 'prev')
        return other


class _ChuckGlobalModule(_ChuckModule):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.modules = []
        self.stream = None

    def append(self, other: '_ChuckModule', which: str):
        with self.lock:
            self.modules.append(other)
            if not self.stream.active:
                self.stream.start()
        threading.current_thread().instance.remember(self, other)

    def remove(self, other: '_ChuckModule'):
        with self.lock:
            self.modules.remove(other)
            if len(self.modules) == 0 and self.stream.active:
                self.stream.stop()


class _ADC(_ChuckGlobalModule):
    def __init__(self):
        super().__init__()
        self.type = _ChuckModuleType.OUT

    def __str__(self):
        return 'adc'

    def compute(self, length: int):
        # TODO: implement
        pass


class _DAC(_ChuckGlobalModule):
    def __init__(self):
        super().__init__()
        self.type = _ChuckModuleType.IN

        self.ready = threading.Event()
        self.go = threading.Event()
        self.buffer = np.zeros(self.buffer_size * 2, dtype=np.float32)
        self.i = 0

        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            channels=1,
            dtype=np.float32,
            callback=self.callback)

    def __str__(self):
        return 'dac'

    def callback(self, outdata, frames, time, status):
        # wait for chuck
        self.ready.wait()
        # copy
        outdata[:] = self.buffer[:frames].reshape(-1, 1)
        # roll
        self.i -= frames
        self.buffer[:self.i] = self.buffer[frames:frames + self.i]
        # notify chuck
        self.ready.clear()
        self.go.set()

    def compute(self, length: int):
        self.buffer[self.i:self.i + length] = 0
        for module in self.modules:
            self.buffer[self.i:self.i + length] += module.compute(length)
        self.i += length
        if self.i >= self.buffer_size:
            self.ready.set()
            self.go.wait()
            self.go.clear()

    def debug(self):
        print([str(module) for module in self.modules])


class _Blackhole(_ChuckGlobalModule):
    def __init__(self):
        super().__init__()
        self.type = _ChuckModuleType.IN

    def __str__(self):
        return 'blackhole'

    def compute(self, length: int):
        # TODO: implement
        pass


class SinOsc(_ChuckModule):
    def __init__(self, freq: float = 440):
        super().__init__()
        self.type = _ChuckModuleType.OUT
        self.next = []
        self.freq = freq
        self.phi = 0

    def __str__(self):
        return f'SinOsc({self.freq})'

    def compute(self, length: int):
        output = librosa.tone(self.freq, sr=self.sample_rate, length=length, phi=self.phi)
        self.phi += 2 * np.pi * self.freq * length / self.sample_rate
        return output


# ======================================================================
# Core
# ======================================================================
def spork(func, *args):
    global __CHUCK__
    threading.Thread(target=__CHUCK__.exec, args=(func, *args)).start()


class _ChuckThread:
    def __init__(self, thread: threading.Thread):
        self.ready = threading.Event()
        self.go = threading.Event()
        self.sample_request = 0
        self.links = []  # remember thread modules connected to global modules
        thread.instance = self

    def remember(self, global_module: _ChuckGlobalModule, module: _ChuckModule):
        self.links.append((global_module, module))

    def remove(self):
        for global_module, module in self.links:
            global_module.remove(module)
        self.links = []

    def wait(self, sample_request: int):
        self.sample_request = sample_request
        self.ready.set()
        self.go.wait()
        self.go.clear()


class _ChuckThreadList:
    def __init__(self):
        self.threads = []
        self.lock = threading.Lock()

    def add(self, thread: threading.Thread):
        with self.lock:
            self.threads.append(_ChuckThread(thread))

    def remove(self, thread: threading.Thread):
        with self.lock:
            self.threads.remove(thread.instance)
            thread.instance.remove()

    def debug(self):
        print([thread.sample_request for thread in self.threads])


class _Chuck:
    def __init__(self, sample_rate=22050, buffer_size=256, verbose=False):
        global __CHUCK__
        __CHUCK__ = self
        # options
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.verbose = verbose
        # members
        self.thread_list = _ChuckThreadList()
        self.now = _ChuckNow()
        self.adc = _ADC()
        self.dac = _DAC()
        self.blackhole = _Blackhole()
        # global
        self.init_global()

    def __str__(self):
        return f"Chuck(sample_rate={self.sample_rate}, buffer_size={self.buffer_size})"

    def init_global(self):
        global now, adc, dac, blackhole
        now = self.now
        adc = self.adc
        dac = self.dac
        blackhole = self.blackhole

    def loop(self):
        if self.verbose:
            print(f"{self} start ...")

        while True:
            # block upcoming threads
            self.thread_list.lock.acquire()

            # no threads
            if len(self.thread_list.threads) == 0:
                self.thread_list.lock.release()
                time.sleep(0.1)
                continue

            # thread not ready
            thread_not_ready = next((thread for thread in self.thread_list.threads if not thread.ready.is_set()), None)
            if thread_not_ready is not None:
                self.thread_list.lock.release()
                thread_not_ready.ready.wait()
                continue

            # all threads ready
            if self.verbose:
                self.debug()

            # compute
            sample_request = min(self.buffer_size, min(thread.sample_request for thread in self.thread_list.threads))
            self.compute(sample_request)

            # update time and threads
            self.now.sample_count += sample_request
            for thread in self.thread_list.threads:
                thread.sample_request -= sample_request
                if thread.sample_request < 1:
                    thread.ready.clear()
                    thread.go.set()

            # unblock upcoming threads
            self.thread_list.lock.release()

    def compute(self, sample_request):
        self.dac.compute(sample_request)
        self.blackhole.compute(sample_request)
        self.adc.compute(sample_request)

    def exec(self, func, *args):
        self.thread_list.add(threading.current_thread())
        func(*args)
        self.thread_list.remove(threading.current_thread())

    def start(self):
        threading.Thread(target=self.loop).start()

    def debug(self):
        print("Graph:")
        self.dac.debug()
        print("Threads:")
        self.thread_list.debug()
