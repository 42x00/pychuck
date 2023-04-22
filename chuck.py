from pychuck.core import _Chuck

app = _Chuck()
app._add_shred(open('examples/tmp.py').read())
app._loop()
