import copy
import json

from stilus.nodes.node import Node


class UnaryOp(Node):

    def __init__(self, op, expr):
        super().__init__()
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

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'UnaryOp',
                           'op': self.op,
                           'expr': self.expr,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
