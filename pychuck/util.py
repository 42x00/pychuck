import ast
from enum import Enum

import pychuck


class _ChuckDurUnit(Enum):
    ms = 1e-3
    s = 1
    m = 60
    h = 3600
    day = 86400
    week = 604800


class _ChuckDur:
    def __init__(self, dur: float, unit: str = 's'):
        if unit == 'samp':
            self._frames = int(dur)
        elif unit in _ChuckDurUnit.__members__:
            self._frames = int(dur * pychuck.__CHUCK__._sample_rate * _ChuckDurUnit[unit].value)
        else:
            raise ValueError(f'Invalid time unit: {unit}')

    def __truediv__(self, other: '_ChuckDur'):
        return self._frames / other._frames

    def __mul__(self, other: float):
        return _ChuckDur(self._frames * other, 'samp')

    def __rshift__(self, other):
        pass


class _ChuckTime:
    def __init__(self, other: '_ChuckTime' = None):
        self._frame = 0
        if other is not None:
            self._frame = other._frame

    def __le__(self, other: '_ChuckTime'):
        return self._frame <= other._frame

    def __lt__(self, other: '_ChuckTime'):
        return self._frame < other._frame

    def __ge__(self, other: '_ChuckTime'):
        return self._frame >= other._frame

    def __gt__(self, other: '_ChuckTime'):
        return self._frame > other._frame

    def __sub__(self, other: '_ChuckTime'):
        return _ChuckDur(self._frame - other._frame, 'samp')


class Time(_ChuckTime):
    pass


class Dur(_ChuckDur):
    pass


class _ChuckCodeTransformer(ast.NodeTransformer):
    # Dur(1, 's') >> now -> yield Dur(1, 's')
    def visit_BinOp(self, node):
        if isinstance(node.op, ast.RShift) and isinstance(node.right, ast.Name) and node.right.id == 'now':
            return ast.Yield(node.left)
        return node

    # delete: from pychuck import *
    def visit_ImportFrom(self, node):
        if node.module != 'pychuck' or node.names[0].name != '*':
            return node


def _code_transform(code: str) -> str:
    wrapper_tree = ast.parse(f'from pychuck import *\ndef __chuck_shred__(): pass')
    code_tree = ast.parse(code)
    ast.fix_missing_locations(_ChuckCodeTransformer().visit(code_tree))
    wrapper_tree.body[1].body = code_tree.body
    return ast.unparse(wrapper_tree)
