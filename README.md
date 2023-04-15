# PyChuck

### Introduction

PyChuck is a Python Library for the [ChucK](http://chuck.cs.princeton.edu/) programming language.

### Usage

```python
from pychuck import *

# compute parameters
freq = 440

# define chuck module and graph
s = SinOsc(freq)
s >> dac

# time control
now += 1 * samp
```

### Quickstart

```bash
git clone https://github.com/42x00/pychuck
cd pychuck

conda create -n pychuck python -y
conda activate pychuck
pip install sounddevice

python chuck.py examples/sinosc.py
```

