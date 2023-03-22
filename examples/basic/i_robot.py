from pychuck import *

g = Gain(gain=0.05)
g2 = Gain(gain=0.05)
g3 = Gain(gain=0.95)
d = Delay(delay=15 * ms)

adc >> g >> d >> dac
adc >> g2 >> dac
d >> g3 >> d

while True:
    now += 100 * ms
