import pychuck

import ast
import types
from enum import Enum


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
            self.frames = int(dur)
        elif unit in _ChuckDurUnit.__members__:
            self.frames = int(dur * pychuck.__CHUCK__.sample_rate * _ChuckDurUnit[unit].value)
        else:
            raise ValueError(f'Invalid time unit: {unit}')

    def __truediv__(self, other: '_ChuckDur'):
        return self.frames / other.frames

    def __mul__(self, other: float):
        return _ChuckDur(self.frames * other, 'samp')

    def __rshift__(self, other):
        pass


class _ChuckTime:
    def __init__(self, other: '_ChuckTime' = None):
        self.frame = 0
        if other is not None:
            self.frame = other.frame

    def __le__(self, other: '_ChuckTime'):
        return self.frame <= other.frame

    def __lt__(self, other: '_ChuckTime'):
        return self.frame < other.frame

    def __ge__(self, other: '_ChuckTime'):
        return self.frame >= other.frame

    def __gt__(self, other: '_ChuckTime'):
        return self.frame > other.frame

    def __sub__(self, other: '_ChuckTime'):
        return _ChuckDur(self.frame - other.frame, 'samp')


class Time(_ChuckTime):
    pass


class Dur(_ChuckDur):
    pass


class _ChuckCodeTransformer(ast.NodeTransformer):
    def visit_BinOp(self, node):
        if isinstance(node.op, ast.RShift) and isinstance(node.right, ast.Name) and node.right.id == 'now':
            return ast.Yield(node.left)
        return node

    def visit_ImportFrom(self, node):
        if node.module != 'pychuck' or node.names[0].name != '*':
            return node


def _code_transform(code: str, shred_id: int):
    main_tree = ast.parse(f'from pychuck import *\ndef _shred_{shred_id}(): pass')
    tree = ast.parse(code)
    ast.fix_missing_locations(_ChuckCodeTransformer().visit(tree))
    main_tree.body[1].body = tree.body
    return ast.unparse(main_tree)


# def _code_transform(code: str, shred_id: int):
#     return code.replace('def main():', f'def _shred_{shred_id}():')


def _code2gen(code_or_gen: str or types.GeneratorType, shred_id: int):
    # check
    if code_or_gen is None or isinstance(code_or_gen, types.GeneratorType):
        return code_or_gen
    # compile
    exec(_code_transform(code_or_gen, shred_id), globals())
    # return generator
    return globals()[f'_shred_{shred_id}']()
