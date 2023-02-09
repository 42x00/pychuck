from pychuck.core import spork
from pychuck.module import SinOsc, Noise, TwoPole
from pychuck.util import Dur, Time

__CHUCK__ = None
now = None
adc = None
dac = None
blackhole = None
