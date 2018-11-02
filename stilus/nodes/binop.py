import copy
import json

from stilus.nodes.node import Node


class BinOp(Node):

    def __init__(self, op, left, right):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return f'({self.left} {self.op} {self.right})'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.op, self.left, self.right

    def __eq__(self, other):
        if isinstance(other, BinOp):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'BinOp',
                           'left': self.left,
                           'right': self.right,
                           'op': self.op,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
