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
Dur(1, "samp") >> now
```

### Quickstart

```bash
git clone https://github.com/42x00/pychuck
cd pychuck

conda create -y -n pychuck -c conda-forge librosa
conda activate pychuck
pip install sounddevice

python chuck.py examples/sinosc.py
```

