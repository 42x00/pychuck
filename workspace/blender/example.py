code = """
from pychuck import *
import bpy

s = SinOsc()
s >> dac

later = now + 5 * second

while now < later:
    now += 200 * samp
    bpy.context.scene.objects["Cube"].location.z = s.last * 10
"""

import pychuck

pychuck.__CHUCK__._add_shred(code)
