import ast
import types


class _ChuckDur:
    def __init__(self, samples: float):
        self._samples = samples

    def __add__(self, other: '_ChuckDur' or '_ChuckTime'):
        if isinstance(other, _ChuckDur):
            return _ChuckDur(self._samples + other._samples)
        elif isinstance(other, _ChuckTime):
            return _ChuckTime(self._samples + other._sample)

    def __sub__(self, other: '_ChuckDur'):
        if isinstance(other, _ChuckDur):
            return _ChuckDur(self._samples - other._samples)

    def __mul__(self, other: float):
        return _ChuckDur(self._samples * other)

    def __rmul__(self, other: float):
        return _ChuckDur(other * self._samples)

    def __truediv__(self, other: float or '_ChuckDur'):
        if isinstance(other, float):
            return _ChuckDur(self._samples / other)
        elif isinstance(other, int):
            return _ChuckDur(self._samples / other)
        elif isinstance(other, _ChuckDur):
            return self._samples / other._samples


class _ChuckTime:
    def __init__(self, sample: float):
        self._sample = sample

    def __str__(self):
        return str(self._sample)

    def __add__(self, other: '_ChuckDur'):
        if isinstance(other, _ChuckDur):
            return _ChuckTime(self._sample + other._samples)

    def __sub__(self, other: '_ChuckDur' or '_ChuckTime'):
        if isinstance(other, _ChuckDur):
            return _ChuckTime(self._sample - other._samples)
        elif isinstance(other, _ChuckTime):
            return _ChuckDur(self._sample - other._sample)

    def __truediv__(self, other: '_ChuckDur'):
        if isinstance(other, _ChuckDur):
            return self._sample / other._samples

    def __mod__(self, other: '_ChuckDur'):
        if isinstance(other, _ChuckDur):
            return _ChuckDur(self._sample % other._samples)

    def __matmul__(self, other: types.GeneratorType):
        pass

    def __lt__(self, other: '_ChuckTime'):
        return self._sample < other._sample

    def __gt__(self, other: '_ChuckTime'):
        return self._sample > other._sample

    def __le__(self, other: '_ChuckTime'):
        return self._sample <= other._sample

    def __ge__(self, other: '_ChuckTime'):
        return self._sample >= other._sample

    def __eq__(self, other: '_ChuckTime'):
        return self._sample == other._sample

    def __ne__(self, other: '_ChuckTime'):
        return self._sample != other._sample

    def copy(self):
        return _ChuckTime(self._sample)


class Std:
    @staticmethod
    def mtof(midi_note: int):
        if midi_note <= -1500:
            return 0
        if midi_note > 1499:
            midi_note = 1499
        return 2 ** ((midi_note - 69) / 12) * 440


class _ChuckCodeTransformer(ast.NodeTransformer):
    # now += 1 * second -> yield 1 * second
    def visit_AugAssign(self, node):
        if isinstance(node.op, ast.Add) and isinstance(node.target, ast.Name) and node.target.id == "now":
            return ast.Expr(value=ast.Yield(value=node.value))
        return node

    # now @ func -> yield from func
    def visit_BinOp(self, node):
        if isinstance(node.op, ast.MatMult) and isinstance(node.left, ast.Name) and node.left.id == "now":
            return ast.Expr(value=ast.YieldFrom(value=node.right))
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
