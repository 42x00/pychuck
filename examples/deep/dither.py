from pychuck import *

imp = Impulse()
s = SinOsc(freq=220)

imp >> dac
s >> blackhole


def play_with_dither(src, T, qbits, do_dither):
    if qbits < 0 or qbits > 24:
        print("quantization bits out of range (1-24)")

    sample = 0
    quantized = 0
    max = 1 << 24

    while T > 0 * second:
        sample = src.last
        if do_dither:
            quantized = int((sample + np.random.uniform(0, 2 ** -qbits)) * max)
        else:
            quantized = int(sample * max)

        quantized = quantized >> (24 - qbits) << (24 - qbits)
        imp.next = quantized / max
        now += 1 * samp
        T -= 1 * samp


now @ play_with_dither(s, 2 * second, 6, False)
now @ play_with_dither(s, 2 * second, 6, True)
now += .5 * second

now @ play_with_dither(s, 2 * second, 5, False)
now @ play_with_dither(s, 2 * second, 5, True)
now += .5 * second

now @ play_with_dither(s, 2 * second, 4, False)
now @ play_with_dither(s, 2 * second, 4, True)
now += .5 * second
