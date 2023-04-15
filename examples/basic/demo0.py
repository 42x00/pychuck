from pychuck import *

later = 5 * second + now

while now < later:
    print(now)
    now += 1 * second

print(now)
