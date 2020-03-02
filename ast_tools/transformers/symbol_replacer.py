import ast
from copy import deepcopy

class SymbolReplacer(ast.NodeTransformer):
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table

    def visit_Name(self, node):
        if node.id in self.symbol_table:
            return deepcopy(self.symbol_table[node.id])
        return node


class SymbolReplacer_2(ast.NodeTransformer):
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table

    def visit_Attribute(self, node):
        if 'symbol_interpolate' in self.symbol_table:
            node.attr = node.attr.replace('symbol_interpolate', str(self.symbol_table['symbol_interpolate'].n))

            if hasattr(node.value, "attr"):
                node.value.attr = node.value.attr.replace('symbol_interpolate', str(self.symbol_table['symbol_interpolate'].n))

        return node


def replace_symbols(tree, symbol_table):
    temp = SymbolReplacer(symbol_table).visit(tree)
    return SymbolReplacer_2(symbol_table).visit(temp)

