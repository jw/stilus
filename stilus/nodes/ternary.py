import json

from stilus.nodes.node import Node


class Ternary(Node):

    def __init__(self, cond, true_expr, false_expr, lineno=1, column=1):
        super().__init__(lineno=lineno, column=1)
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

    def clone(self, parent=None, node=None):
        clone = Ternary(None, None, None,
                        lineno=self.lineno, column=self.column)
        clone.cond = self.cond.clone(parent, clone)
        clone.true_expr = self.true_expr.clone(parent, clone)
        clone.false_expr = self.false_expr.clone(parent, clone)
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'UnaryOp',
                           'op': self.op,
                           'expr': self.expr,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
