import pychuck

import ast
from enum import Enum


class _ChuckDurUnit(Enum):
    ms = 1e-3
    s = 1
    m = 60
    h = 3600
    day = 86400
    week = 604800


class Dur:
    def __init__(self, dur: float, unit: str = 's'):
        self.frames = dur * pychuck.__CHUCK__.sample_rate
        if unit == 'samp':
            self.frames = int(dur)
        elif unit in _ChuckDurUnit.__members__:
            self.frames = int(self.frames * _ChuckDurUnit[unit].value)
        else:
            raise ValueError(f'Invalid time unit: {unit}')
        if self.frames <= 0:
            raise ValueError(f'Duration must be positive, but got {dur} {unit}')

    def __rshift__(self, other):
        pass


class _ChuckNow:
    def __init__(self):
        self.frame = 0


class _ChuckCodeTransformer(ast.NodeTransformer):
    def visit_BinOp(self, node):
        if isinstance(node.op, ast.RShift) and isinstance(node.right, ast.Name) and node.right.id == 'now':
            return ast.Yield(node.left)
        return node

    def visit_ImportFrom(self, node):
        if node.module != 'pychuck' or node.names[0].name != '*':
            return node


def _code_transform(code: str, shred_id: int):
    main_tree = ast.parse(f'from pychuck import *\ndef _chuck_shred_{shred_id}(): pass')
    tree = ast.parse(code)
    ast.fix_missing_locations(_ChuckCodeTransformer().visit(tree))
    main_tree.body[1].body = tree.body
    return ast.unparse(main_tree)
