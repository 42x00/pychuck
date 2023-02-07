from pychuck import *
from pynput import keyboard
from numpy import interp


def play_key(c):
    freq = interp(ord(c), [97, 122], [220, 880])
    s = SinOsc(freq=freq)
    s >> dac
    Dur(80, "ms") >> now


def on_press(key):
    if hasattr(key, "char"):
        spork(play_key, key.char)


def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False


# # Collect events until released
# with keyboard.Listener(
#         on_press=on_press,
#         on_release=on_release) as listener:
#     listener.join()

# ...or, in a non-blocking fashion:
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()
