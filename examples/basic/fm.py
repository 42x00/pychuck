from pychuck import *

# carrier
c = SinOsc()
c >> dac
# modulator
m = SinOsc()
m >> blackhole

# carrier frequency
cf = 220
# modulator frequency
m.freq = mf = 550
# index of modulation
index = 200

# time-loop
while True:
    # modulate
    c.freq = cf + (index * m.last)
    # advance time by 1 samp
    now += 1 * samp
