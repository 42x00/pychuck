import time

import numpy as np

from pychuck.core import _Chuck

app = _Chuck()
app._add_shred(open('examples/tmp.py').read())

interval = app._buffer_size / app._sample_rate
indata = np.zeros(app._buffer_size)

while True:
    outdata = app._forward(indata)
    time.sleep(interval)
