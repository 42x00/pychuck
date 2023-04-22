import ast


class _ChuckTime:
    def __init__(self, sample: int):
        self._sample = sample


class _ChuckDur:
    def __init__(self, samples: float):
        self._samples = samples

    def __truediv__(self, other: float) -> '_ChuckDur':
        return _ChuckDur(self._samples / other)

    def __mul__(self, other: float) -> '_ChuckDur':
        return _ChuckDur(self._samples * other)


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


def _wrap_code(code: str) -> str:
    wrapper_tree = ast.parse(f'from pychuck import *\ndef __chuck_shred__(): pass')
    code_tree = ast.parse(code)
    ast.fix_missing_locations(_ChuckCodeTransformer().visit(code_tree))
    wrapper_tree.body[1].body = code_tree.body
    return ast.unparse(wrapper_tree)
