from pychuck import *

from pynput import keyboard
from numpy import interp

s = SinOsc()
s >> dac


def on_press(key):
    if hasattr(key, "char"):
        s.freq = interp(ord(key.char), [97, 122], [30, 1000])


listener = keyboard.Listener(on_press=on_press)
listener.start()

Dur(1, "day") >> now
