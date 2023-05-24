Tutorial
========

Terminal
--------

.. code-block::

    # pychuck --help
    pychuck demo.py

Time Control
------------
.. code-block::

    from pychuck import *

    later = now + 5 * second

    while now < later:
        print(now)
        1 * second >> now

Unit Control
------------
.. code-block::

    from pychuck import *

    # graph
    adc >> dac

    # main loop
    while True:
        1 * second >> now

Example
-------
.. code-block::

    from pychuck import *

    # unit
    s = SinOsc(freq=440)

    # graph
    s >> dac

    # main loop
    while True:
        # parameter
        s.freq = np.random.randint(100, 1000)
        # time
        200 * ms >> now

Custom Unit
-----------
.. code-block::

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