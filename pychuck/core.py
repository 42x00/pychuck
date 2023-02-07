import pychuck
from pychuck.module import _ChuckGlobalModule, _ChuckModule, _ADC, _DAC, _Blackhole
from pychuck.util import _ChuckNow

import time
import threading


def spork(func, *args):
    threading.Thread(target=pychuck.__CHUCK__.exec, args=(func, *args)).start()


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
        self.ready.set()

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
        pychuck.__CHUCK__ = self
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
        pychuck.now = self.now
        pychuck.adc = self.adc
        pychuck.dac = self.dac
        pychuck.blackhole = self.blackhole

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
