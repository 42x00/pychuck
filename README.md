# PyChucK

### Installation

```bash
pip install pychuck
```

### Usage

```python
# demo.py
from pychuck import *


# Custom UGen
class Noise(UGen):
    def _tick(self, samples: int) -> np.ndarray:
        return np.random.uniform(-1, 1, samples)


# Graph
n = Noise()
n >> dac

# Main loop
while True:
    # Adjust Parameters
    n.gain = np.random.uniform(0, 1)
    # Time Control
    200 * ms >> now
```

### Quick Start

```bash
# pychuck --help
pychuck demo.py
```

        
        
       