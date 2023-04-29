# PyChucK

### Introduction

PyChucK is a Python Implementation for [ChucK](https://chuck.stanford.edu/)

### Usage

```python
from pychuck import *

# patch
s = SinOsc(gain=.5)
s >= dac

# update
while True:
    s.freq = np.random.randint(30, 1000)
    now += 200 * ms
```

### Quickstart

```bash
git clone https://github.com/42x00/pychuck && cd pychuck
pip install sounddevice
python chuck.py examples/sinosc.py
```

