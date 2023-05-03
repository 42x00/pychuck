from pychuck import *

g = SinOsc()
fft = FFT()

g >> fft >> blackhole

srate = second / samp
fft.size = 8

div = 0
while True:
    g.freq = srate / fft.size * div
    div = (div + 1) % (fft.size / 2)

    fft.upchuck()
    print(fft.spectrum)

    now += 100 * ms
