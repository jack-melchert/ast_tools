import ast
import typing as tp

from . import Pass
from . import PASS_ARGS_T

from ast_tools.stack import get_symbol_table, SymbolTable
from ast_tools.common import get_ast, exec_def_in_file

__ALL__ = ['begin_rewrite', 'end_rewrite']

class begin_rewrite:
    """
    begins a chain of passes
    """
    def __init__(self):
        env = get_symbol_table([self.__init__])
        self.env = env

    def __call__(self, fn) -> PASS_ARGS_T:
        tree = get_ast(fn)
        return tree, self.env

def _issubclass(t, s) -> bool:
    try:
        return issubclass(t, s)
    except TypeError:
        return False


class end_rewrite(Pass):
    """
    ends a chain of passes
    """
    def __init__(self, path: tp.Optional[str] = None):
        self.path = path

    def rewrite(self,
            tree: ast.AST,
            env: SymbolTable) -> tp.Union[tp.Callable, type]:
        decorators = []
        first_group = True
        in_group = False
        # filter passes from the decorator list
        for node in reversed(tree.decorator_list):
            if not first_group:
                decorators.append(node)
                continue

            if isinstance(node, ast.Call):
                name = node.func.id
            else:
                assert isinstance(node, ast.Name)
                name = node.id

            deco = env[name]
            if in_group:
                if  _issubclass(deco, end_rewrite):
                    assert in_group
                    in_group = False
                    first_group = False
            elif _issubclass(deco, begin_rewrite):
                assert not in_group
                in_group = True
            else:
                decorators.append(node)

        tree.decorator_list = reversed(decorators)
        tree = ast.fix_missing_locations(tree)
        return exec_def_in_file(tree, env, self.path)
