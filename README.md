# PyChuck

### Introduction

PyChuck is a Python Library for the [ChucK](http://chuck.cs.princeton.edu/) programming language.

### Usage

```python
from pychuck import *


def main():
    # compute parameters
    freq = 440

    # define chuck module and graph
    s = SinOsc(freq)
    s >> dac

    # time control
    yield Dur(1, "s")
```

### Quickstart

```bash
git clone https://github.com/42x00/pychuck
cd pychuck

conda create -y -n pychuck -c conda-forge librosa
conda activate pychuck

python chuck.py examples/sinosc.py
```

