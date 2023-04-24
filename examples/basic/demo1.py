from pychuck import *

t = a = 0
b = 1
c = 15

while c > 0:
    t = a + b
    a = b
    b = t
    print(b)
    c -= 1

