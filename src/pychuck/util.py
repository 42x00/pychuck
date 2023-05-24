import ast
from enum import Enum

import pychuck
from .unit import _ADC, _DAC, _Blackhole


def spork(generator):
    current_shred = pychuck.me
    current_shred._shreds.append(pychuck.core._Shred(generator))
    pychuck.me = current_shred


class _Event(Enum):
    ADD_SHRED = 0
    REPLACE_SHRED = 1
    REMOVE_SHRED = 2
    REMOVE_LAST_SHRED = 3
    CLEAR_VM = 4


class _Time:
    def __init__(self, value: float):
        self._value = value

    def __rshift__(self, other):
        raise NotImplementedError

    def __add__(self, other: '_Dur') -> '_Time':
        if isinstance(other, _Dur):
            return _Time(self._value + other._value)
        else:
            raise TypeError

    def __sub__(self, other: '_Time' or '_Dur') -> '_Dur' or '_Time':
        if isinstance(other, _Time):
            return _Dur(self._value - other._value)
        elif isinstance(other, _Dur):
            return _Time(self._value - other._value)
        else:
            raise TypeError

    def __lt__(self, other: '_Time') -> bool:
        if isinstance(other, _Time):
            return self._value < other._value
        else:
            raise TypeError

    def __le__(self, other: '_Time') -> bool:
        if isinstance(other, _Time):
            return self._value <= other._value
        else:
            raise TypeError

    def __eq__(self, other: '_Time') -> bool:
        if isinstance(other, _Time):
            return self._value == other._value
        else:
            raise TypeError

    def __ne__(self, other: '_Time') -> bool:
        if isinstance(other, _Time):
            return self._value != other._value
        else:
            raise TypeError

    def __gt__(self, other: '_Time') -> bool:
        if isinstance(other, _Time):
            return self._value > other._value
        else:
            raise TypeError

    def __ge__(self, other: '_Time') -> bool:
        if isinstance(other, _Time):
            return self._value >= other._value
        else:
            raise TypeError

    def __str__(self) -> str:
        return str(self._value)


class _Dur:
    def __init__(self, value: float):
        self._value = value

    def __add__(self, other: '_Dur' or '_Time') -> '_Dur' or '_Time':
        if isinstance(other, _Dur):
            return _Dur(self._value + other._value)
        elif isinstance(other, _Time):
            return _Time(self._value + other._value)
        else:
            raise TypeError

    def __sub__(self, other: '_Dur') -> '_Dur':
        if isinstance(other, _Dur):
            return _Dur(self._value - other._value)
        else:
            raise TypeError

    def __mul__(self, other: float) -> '_Dur':
        return _Dur(self._value * other)

    def __rmul__(self, other: float) -> '_Dur':
        return _Dur(self._value * other)

    def __truediv__(self, other: '_Dur' or float) -> float or '_Dur':
        if isinstance(other, _Dur):
            return self._value / other._value
        else:
            return _Dur(self._value / other)

    def __lt__(self, other: '_Dur') -> bool:
        if isinstance(other, _Dur):
            return self._value < other._value
        else:
            raise TypeError

    def __le__(self, other: '_Dur') -> bool:
        if isinstance(other, _Dur):
            return self._value <= other._value
        else:
            raise TypeError

    def __eq__(self, other: '_Dur') -> bool:
        if isinstance(other, _Dur):
            return self._value == other._value
        else:
            raise TypeError

    def __ne__(self, other: '_Dur') -> bool:
        if isinstance(other, _Dur):
            return self._value != other._value
        else:
            raise TypeError

    def __gt__(self, other: '_Dur') -> bool:
        if isinstance(other, _Dur):
            return self._value > other._value
        else:
            raise TypeError

    def __ge__(self, other: '_Dur') -> bool:
        if isinstance(other, _Dur):
            return self._value >= other._value
        else:
            raise TypeError

    def __int__(self) -> int:
        return int(self._value)

    def __str__(self) -> str:
        return str(self._value)


class _CodeTransformer(ast.NodeTransformer):
    # 1 * second >> now -> yield 1 * second
    # func() >> now -> yield from func()
    def visit_Expr(self, node):
        if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.RShift) \
                and isinstance(node.value.right, ast.Name) and node.value.right.id == 'now':
            if isinstance(node.value.left, ast.Call):
                return ast.Expr(value=ast.YieldFrom(value=node.value.left))
            else:
                return ast.Expr(value=ast.Yield(value=node.value.left))
        return node

    # delete: from pychuck import *
    def visit_ImportFrom(self, node):
        if node.module != 'pychuck' or node.names[0].name != '*':
            return node


def _wrap_code(code: str) -> str:
    wrapper_tree = ast.parse("""
from pychuck import *
def __shred__():
    pass
""")
    code_tree = ast.parse(code)
    ast.fix_missing_locations(_CodeTransformer().visit(code_tree))
    wrapper_tree.body[1].body = code_tree.body
    return ast.unparse(wrapper_tree)


def _init_globals(sample_rate: int):
    pychuck.adc = _ADC()
    pychuck.dac = _DAC()
    pychuck.blackhole = _Blackhole()
    pychuck.now = _Time(0)
    pychuck.samp = _Dur(1)
    pychuck.second = _Dur(sample_rate)
    pychuck.ms = pychuck.second / 1000
    pychuck.minute = pychuck.second * 60
    pychuck.hour = pychuck.minute * 60
    pychuck.day = pychuck.hour * 24
    pychuck.week = pychuck.day * 7
