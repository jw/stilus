import copy
import json

from stilus.nodes.node import Node


class Ternary(Node):

    def __init__(self, cond, true_expr, false_expr):
        super().__init__()
        self.cond = cond
        self.true_expr = true_expr
        self.false_expr = false_expr

    def __str__(self):
        return f'({self.cond},{self.true_expr},{self.false_expr})'

    def __repr__(self):
        return [n.__str__() for n in self.nodes]

    def __key(self):
        return self.cond, self.true_expr, self.false_expr

    def __eq__(self, other):
        if isinstance(other, Ternary):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'UnaryOp',
                           'op': self.op,
                           'expr': self.expr,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
