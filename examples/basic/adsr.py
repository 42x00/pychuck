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
s = SinOsc(gain=0.5)
e = ADSR(A=10 * ms, D=8 * ms, S=0.5, R=500 * ms)
# (note: A, D, R are durations; S is a number between 0 and 1)
s >> e >> dac

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
    now += 500 * ms
    #  key off; start RELEASE
    e.keyOff()
    #  allow the RELEASE to ramp down to 0
    now += e.releaseTime()
    #  advance time by 300 ms (duration until the next sound)
    now += 300 * ms
