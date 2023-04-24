from pychuck import *

a = 8


def abs(v: int) -> int:
    if v < 0:
        return -v
    return v


def args(y: int, b: int):
    a = 4
    print(b)


def sum(a: float, b: float) -> float:
    return a + b


def go(a: int):
    print(abs(a))
    if a == 0:
        return
    go(abs(a) - 1)


for i in range(10):
    go(1000)
print(abs(-1))
args(1, 2)
print(sum(1., 2.))
print(a)
