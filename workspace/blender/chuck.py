import threading
import sys

sys.path.append('/Users/ykli/research/pychuck')
from pychuck.core import _Chuck

app = _Chuck()
threading.Thread(target=app._start).start()
