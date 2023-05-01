from pychuck import *

R = .99999
L = 500

imp = Noise()
lowpass = OneZero()
delay = Delay(delay=L * samp, gain=R ** L)

imp >> lowpass >> dac
lowpass >> delay >> lowpass

lowpass.zero = -1
imp.gain = 1
now += L * samp
imp.gain = 0

now += (np.log(.0001) / np.log(R)) * samp
