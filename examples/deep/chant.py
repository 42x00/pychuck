from pychuck import *

global modphase, period, targetPeriod, f1freq, target_f1freq, f2freq, target_f2freq, f3freq, target_f3freq

# --------------------------------------------------------------------
# name: chant.ck
# desc: chant synthesizer demonstrates multi-shredded concurrency,
#       variable rates, source-filter model, and interpolation.
#
# This is a classic source-filter model for rudimentary singing
# synthesis: an impulse train (the "source", crudely modeling
# opening/closing of the glottis in the vocal tract) going through
# a bank of three formant filters (roughly modeling the filtering
# by the vocal cavity to induce the perception of different vowels).
#
# This example demonstrates an elegant way to implement the above
# in ChucK, by breaking up the tasks into three concurrent shreds:
#   1. a main shred selects the next target pitch and formants
#   2. doImpulse() generates the impulse train using ChucK's
#      strongly-timed mechanisms to modulate the impulse train
#      period to create vibrato
#   3. doInterpolation() interpolates the period and formants,
#      to smoothly glide from note to note, vowel to vowel
#
# author: Perry R. Cook (2006)
#         modified by Rebecca Fiebrink and Ge Wang (2007, 2021)
#         published in ChucK examples 2021
# --------------------------------------------------------------------

# synthesis patch
(i := Impulse()) >> (t := TwoZero()) >> (t2 := TwoZero()) >> (p := OnePole())
# formant filters
p >> (f1 := TwoPole()) >> (g := Gain())
p >> (f2 := TwoPole()) >> g
p >> (f3 := TwoPole()) >> g
# reverbs
g >> (r := JCRev()) >> dac
g >> (rL := JCRev()) >> dac.left
g >> (rR := JCRev()) >> dac.right
# delays
g >> (d1 := Delay()) >> (g1 := Gain()) >> r
g >> (d2 := Delay()) >> (g2 := Gain()) >> rL
g >> (d3 := Delay()) >> (g3 := Gain()) >> rR
# connect gains to delays
g1 >> d1
g2 >> d2
g3 >> d3

# source gain (amplitude of the impulse train)
sourceGain = 0.25

# set filter coefficients
t.b0 = 1.0
t.b1 = 0.0
t.b2 = -1.0

t2.b0 = 1.0
t2.b1 = 0.0
t2.b2 = 1.0

# set gains
g1.gain = 0.1
g2.gain = 0.1
g3.gain = 0.1

# set reverb mix
r.mix = 0.025

# set delay max and length
d1.max = 1.5 * second

d2.max = 2.0 * second

d3.max = 2.8 * second

d1.delay = 1.41459 * second

d2.delay = 1.97511 * second

d3.delay = 2.71793 * second

# set two pole filter radii and gain
f1.radius = 0.997
f2.radius = 0.997
f3.radius = 0.997

f1.gain = 1.0
f2.gain = 0.8
f3.gain = 0.6

# randomize initial formant frequencies
f1.freq = np.random.uniform(230.0, 660.0)

f2.freq = np.random.uniform(800.0, 2300.0)

f3.freq = np.random.uniform(1700.0, 3000.0)

# variables for interpolating current and target formant frequencies
f1freq = 400.0
f2freq = 1000.0
f3freq = 2800.0
target_f1freq = 400.0
target_f2freq = 1000.0
target_f3freq = 2800.0

# leaky integrator
p.pole = 0.99

p.gain = 1.0

# variables that control impulse train source
period = 0.013
targetPeriod = 0.013
modphase = 0.0
vibratoDepth = 0.0001

# scale
scale = [0, 1, 5, 7,
         8, 11, 8, 7,
         11, 12, 14, 15,
         19, 17, 20, 24]
# names (for printing)
names = ["ut0", "ra0", "fa0", "ut0",
         "ra0", "mi0", "ra1", "ut1",
         "mi0", "ut1", "re1", "mi1",
         "ut1", "fa1", "re1", "ut2"]
# current location in scale
scalepoint = 9

# frequency
theFreq = 0


# entry point for shred: generate source impulse train
def doImpulse():
    global modphase
    # infinite time-loop
    while True:
        # fire impulse
        i.next = sourceGain
        # phase variable
        modphase += period
        # vibrato depth
        vibratoDepth = 0.0001
        # modulate wait time until next impulse: vibrato
        now += (period + vibratoDepth * np.sin(2 * np.pi * modphase * 6.0)) * second


# entry point for shred: interpolate period and formant frequencies
def doInterpolation(T):
    global period, targetPeriod, f1freq, target_f1freq, f2freq, target_f2freq, f3freq, target_f3freq
    # percentage progress per time slice
    slew = 0.10
    # infinite time-loop
    while True:
        # go towards target period (pitch)
        period = (targetPeriod - period) * slew + period
        # go towards targat formant frequencies
        f1.freq = f1freq = (target_f1freq - f1freq) * slew + f1freq
        f2.freq = f2freq = (target_f2freq - f2freq) * slew + f2freq
        f3.freq = f3freq = (target_f3freq - f3freq) * slew + f3freq

        # interpolation rate
        now += T


spork(doImpulse())
spork(doInterpolation(10 * ms))

# main shred loop
while True:
    # determine new formant targets
    target_f1freq = np.random.uniform(230.0, 660.0)

    target_f2freq = np.random.uniform(800.0, 2300.0)

    target_f3freq = np.random.uniform(1700.0, 3000.0)

    # next pitch (random walk the scale)
    scalepoint = np.random.randint(-1, 2) + scalepoint

    if scalepoint < 0:
        scalepoint = 0
    if scalepoint > 15:
        scalepoint = 15
    # compute the frequency
    theFreq = Std.mtof(32 + scale[scalepoint])
    # print things for fun
    print(names[scalepoint], theFreq)
    # calculate corresponding target period
    targetPeriod = 1.0 / theFreq

    # wait until next note
    now += np.random.uniform(0.2, 0.9) * second
