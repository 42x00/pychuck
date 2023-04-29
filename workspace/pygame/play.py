import pygame
from pychuck import *

key2note = {'a': 60, 'w': 61, 's': 62, 'e': 63, 'd': 64, 'f': 65, 't': 66, 'g': 67, 'y': 68, 'h': 69, 'u': 70, 'j': 71,
            'k': 72, 'o': 73, 'l': 74, 'p': 75, }


def play(key):
    s = SinOsc(freq=Std.mtof(key), gain=.5)
    e = ADSR(10 * ms, 200 * ms, .5, 200 * ms)
    s >= e >= dac
    e.keyOn()
    now += 300 * ms
    e.keyOff()
    now += 300 * ms


while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            if key_name in key2note:
                spork(play(key2note[key_name]))

    now += 10 * ms
