"""
 name: adsr.py
 desc: ADSR envelope example
     (A)ttack: duration of initial attack
     (D)ecay: duration of decay
     (S)ustain: the level of the sustain
     (R)elease: duration the release

 for more info on envelopes and ADSRs see:
     https:en.wikipedia.org/wiki/Envelope_(music)
     https:en.wikipedia.org/wiki/Envelope_(music)#ADSR
"""
import random

from pychuck import *

#  our patch
(s := SinOsc()) >> (e := ADSR()) >> dac

#  set A, D, S, and R
e.set(A=Dur(10, ms),
      D=Dur(8, ms),
      S=0.5,  # (note: A, D, R are durations; S is a number between 0 and 1)
      R=Dur(500, ms))

#  set gain
s.gain = 0.5

#  infinite time-loop
while True:
    #  choose freq
    s.freq = Std.mtof(random.randint(32, 96))

    #  key on: begin ATTACK
    #  (note: ATTACK automatically transitions to DECAY;
    #         DECAY automatically transitions to SUSTAIN)
    e.keyOn()
    #  advance time by 500 ms
    #  (note: this is the duration from the
    #         beginning of ATTACK to the end of SUSTAIN)
    Dur(500, ms) >> now
    #  key off; start RELEASE
    e.keyOff()
    #  allow the RELEASE to ramp down to 0
    e.releaseTime() >> now

    #  advance time by 300 ms (duration until the next sound)
    Dur(300, ms) >> now
