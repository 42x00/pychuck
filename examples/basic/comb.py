from pychuck import *

R = .99999
L = 500

imp = Impulse()
out = Gain()
delay = Delay(delay=L * samp, gain=R ** L)

imp >> out >> dac
out >> delay >> out

imp.next = 1
now += (np.log(.0001) / np.log(R)) * samp
