import json

from stilus.nodes.node import Node


class UnaryOp(Node):

    def __init__(self, op, expr, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.op = op
        self.expr = expr

    def __str__(self):
        return f'({self.op},{self.expr})'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.op, self.expr

    def __eq__(self, other):
        if isinstance(other, UnaryOp):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self, parent=None, node=None):
        clone = UnaryOp(self.op, None, lineno=self.lineno, column=self.column)
        clone.expr = self.expr.clone(parent, node)
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'UnaryOp',
                           'op': self.op,
                           'expr': self.expr,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
