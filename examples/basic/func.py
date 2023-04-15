from pychuck import *

a = 8


def abs(v):
    if v < 0:
        return -v
    return v


def args(y, b):
    a = 4
    print(b)


def sum(a, b):
    return a + b


def go(a):
    print(abs(a))
    if (a == 0):
        return
    go(abs(a) - 1)


for i in range(10):
    go(1000)

print(abs(-1))
args(1, 2)
print(sum(1.0, 2.0))
print(a)
