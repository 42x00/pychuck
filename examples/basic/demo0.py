from pychuck import *

later = now + 5 * second

while now < later:
    print(now)
    now += 1 * second

print(now)