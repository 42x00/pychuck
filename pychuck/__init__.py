from pychuck.core import spork
from pychuck.module import *
from pychuck.module import _ADC, _DAC, _Blackhole
from pychuck.util import *
from pychuck.util import _ChuckTime, _ChuckDur

__CHUCK__ = None

adc: _ADC = None
dac: _DAC = None
blackhole: _Blackhole = None

now: _ChuckTime = None

samp: _ChuckDur = None
ms: _ChuckDur = None
second: _ChuckDur = None
minute: _ChuckDur = None
hour: _ChuckDur = None
day: _ChuckDur = None
week: _ChuckDur = None

canvas = None
