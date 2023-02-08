from pychuck import *
from pynput import keyboard
from numpy import interp

s = SinOsc()


def main():
    s >> dac
    yield Dur(1, "day")


def on_press(key):
    if hasattr(key, "char"):
        s.freq = interp(ord(key.char), [97, 122], [30, 1000])


listener = keyboard.Listener(on_press=on_press)
listener.start()
