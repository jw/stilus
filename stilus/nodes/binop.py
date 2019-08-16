import json

from stilus.nodes.node import Node


class BinOp(Node):

    def __init__(self, op, left, right=None, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
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
            return True
            # return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self, parent=None, node=None):
        clone = BinOp(self.op, None)
        clone.left = None
        if self.left:
            clone.left = self.left.clone(parent, node)
        clone.right = None
        if self.right:
            clone.right = self.right.clone(parent, node)
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        if self.value:
            clone.value = self.value.clone(parent, node)
        return clone

    def to_json(self):
        return json.dumps({'__type': 'BinOp',
                           'left': self.left,
                           'right': self.right,
                           'op': self.op,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
