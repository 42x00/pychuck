from pychuck import *

now += second - (now % second)

while True:
    print(f'tick: {int(now / second)} seconds')
    now += 1 * second
