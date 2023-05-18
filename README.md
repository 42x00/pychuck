# PyChucK

### Installation

```bash
pip install pychuck
```

### Quickstart

```python
# demo.py
from pychuck import *


# custom unit
class Noise(UGen):
    # generator
    def _tick(self, samples: int) -> np.ndarray:
        return np.random.uniform(-1, 1, samples)


# unit
n = Noise(gain=0.5)

# graph
n >> dac

# main loop
while True:
    # parameter
    n.gain = np.random.uniform(0, 1)
    # time
    200 * ms >> now
```

```bash
# pychuck --help
pychuck demo.py
```

        
        
       