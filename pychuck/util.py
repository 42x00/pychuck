import ast
import ctypes
import inspect
import os

import pychuck


def spork(generator, VM=None):
    current_shred = VM._current_shred
    current_shred._sporks.append(pychuck.core._ChuckShred(VM=VM, generator=generator))
    VM._current_shred = current_shred


class Std:
    @staticmethod
    def mtof(midi_note: int):
        if midi_note <= -1500:
            return 0
        if midi_note > 1499:
            midi_note = 1499
        return 2 ** ((midi_note - 69) / 12) * 440


class _ChuckTime:
    def __init__(self, sample: float):
        self._sample = sample

    def __add__(self, other: '_ChuckDur') -> '_ChuckTime':
        return _ChuckTime(self._sample + other._samples)

    def __sub__(self, other: '_ChuckDur' or '_ChuckTime') -> '_ChuckDur' or '_ChuckTime':
        if isinstance(other, _ChuckDur):
            return _ChuckTime(self._sample - other._samples)
        else:
            return _ChuckDur(self._sample - other._sample)

    def __truediv__(self, other: '_ChuckDur') -> float:
        return self._sample / other._samples

    def __mod__(self, other: '_ChuckDur') -> '_ChuckDur':
        return _ChuckDur(self._sample % other._samples)

    def __lt__(self, other: '_ChuckTime') -> bool:
        return self._sample < other._sample

    def __le__(self, other: '_ChuckTime') -> bool:
        return self._sample <= other._sample

    def __eq__(self, other: '_ChuckTime') -> bool:
        return self._sample == other._sample

    def __ne__(self, other: '_ChuckTime') -> bool:
        return self._sample != other._sample

    def __gt__(self, other: '_ChuckTime') -> bool:
        return self._sample > other._sample

    def __ge__(self, other: '_ChuckTime') -> bool:
        return self._sample >= other._sample

    def __str__(self) -> str:
        return str(self._sample)

    def copy(self):
        return _ChuckTime(self._sample)


class _ChuckDur:
    def __init__(self, samples: float):
        self._samples = samples

    def __add__(self, other: '_ChuckDur' or '_ChuckTime') -> '_ChuckDur' or '_ChuckTime':
        if isinstance(other, _ChuckDur):
            return _ChuckDur(self._samples + other._samples)
        else:
            return _ChuckTime(self._samples + other._sample)

    def __sub__(self, other: '_ChuckDur') -> '_ChuckDur':
        return _ChuckDur(self._samples - other._samples)

    def __mul__(self, other: float) -> '_ChuckDur':
        return _ChuckDur(self._samples * other)

    def __rmul__(self, other: float) -> '_ChuckDur':
        return _ChuckDur(self._samples * other)

    def __truediv__(self, other: float or '_ChuckDur') -> float:
        if isinstance(other, _ChuckDur):
            return self._samples / other._samples
        else:
            return _ChuckDur(self._samples / other)

    def __lt__(self, other: '_ChuckDur') -> bool:
        return self._samples < other._samples

    def __le__(self, other: '_ChuckDur') -> bool:
        return self._samples <= other._samples

    def __eq__(self, other: '_ChuckDur') -> bool:
        return self._samples == other._samples

    def __ne__(self, other: '_ChuckDur') -> bool:
        return self._samples != other._samples

    def __gt__(self, other: '_ChuckDur') -> bool:
        return self._samples > other._samples

    def __ge__(self, other: '_ChuckDur') -> bool:
        return self._samples >= other._samples

    def __int__(self):
        return int(self._samples)

    def copy(self):
        return _ChuckDur(self._samples)


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

    # SinOsc() -> SinOsc(VM=VM)
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and (hasattr(pychuck.module, node.func.id) or node.func.id == 'spork'):
            node.keywords.append(ast.keyword(arg='VM', value=ast.Name(id='VM', ctx=ast.Load())))
        return node

    # delete: from pychuck import *
    def visit_ImportFrom(self, node):
        if node.module != 'pychuck' or node.names[0].name != '*':
            return node


def _wrap_code(code: str) -> str:
    wrapper_tree = ast.parse(f'''
from pychuck import *
def __chuck_shred__(VM, adc, dac, blackhole, now, samp, ms, second, minute, hour, day, week, canvas):
    pass
''')
    code_tree = ast.parse(code)
    ast.fix_missing_locations(_ChuckCodeTransformer().visit(code_tree))
    wrapper_tree.body[1].body = code_tree.body
    return ast.unparse(wrapper_tree)


def _load_stk(compile=True, root='/Users/ykli/research/pychuck/workspace/wrapper'):
    ck2stk = {'SinOsc': 'SineWave'}
    so_path = os.path.join(root, 'libstk_wrapper.so')
    doc = {}
    for cls in pychuck.module._STK.__subclasses__():
        cls_name = ck2stk[cls.__name__] if cls.__name__ in ck2stk else cls.__name__
        cls_doc = {'ctor': ('p', []), 'dtor': ('v', ['p']), 'tick': ('f', ['p', 'f'])}
        for node in ast.walk(ast.parse(inspect.getsource(cls))):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) \
                    and isinstance(node.value.func, ast.Attribute) \
                    and node.value.func.attr.startswith(f'{cls_name}_'):
                fname = node.value.func.attr.split('_')[-1]
                if fname == 'ctor':
                    continue
                restype = node.targets[0].id
                argtypes = [n.func.id for n in node.value.args if isinstance(n, ast.Call)]
                cls_doc[fname] = (restype[0], ['p'] + [t[0] for t in argtypes])
        doc[cls_name] = cls_doc

    if compile:
        cpp_type_map = {'v': 'void', 'f': 'double', 'i': 'int', 'p': '', }
        cpp_code = ""
        for k, v in doc.items():
            cpp_code += f'#include "{k}.h"\n'
        cpp_code += 'extern "C" {\n'
        for k, v in doc.items():
            cpp_type_map['p'] = f'stk::{k}*'
            cpp_code += f'\n\t// {k}'
            for fname, (restype, argtypes) in v.items():
                cpp_code += f"""
    {cpp_type_map[restype]} {k}_{fname}({', '.join([f'{cpp_type_map[t]} arg{i}' for i, t in enumerate(argtypes)])}) {{
"""
                if fname == 'ctor':
                    cpp_code += f'\t\treturn new stk::{k}();\n'
                elif fname == 'dtor':
                    cpp_code += f'\t\tdelete arg0;\n'
                else:
                    if restype == 'v':
                        cpp_code += '\t\t'
                    else:
                        cpp_code += '\t\treturn '
                    cpp_code += f'arg0->{fname}({", ".join([f"arg{i + 1}" for i in range(len(argtypes) - 1)])});\n'
                cpp_code += '\t}\n'
        cpp_code += '}'
        cpp_path = os.path.join(root, 'libstk_wrapper.cpp')
        include_path = os.path.join(root, 'stk', 'include')
        with open(cpp_path, 'w') as f:
            f.write(cpp_code)
        os.system(f'g++ -shared -o {so_path} {cpp_path} -I{include_path} -lstk -fPIC')

    libstk_wrapper = ctypes.CDLL(so_path)
    py_type_map = {'f': ctypes.c_double, 'i': ctypes.c_ulong, 'p': ctypes.c_void_p, }
    for k, v in doc.items():
        for fname, (restype, argtypes) in v.items():
            if restype != 'v':
                getattr(libstk_wrapper, f'{k}_{fname}').restype = py_type_map[restype]
            if len(argtypes) > 0:
                getattr(libstk_wrapper, f'{k}_{fname}').argtypes = [py_type_map[t] for t in argtypes]
    return libstk_wrapper
