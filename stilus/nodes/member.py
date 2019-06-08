import json

from stilus.nodes.node import Node


class Member(Node):

    def __init__(self, left, right, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.right = right
        self.left = left

    def __str__(self):
        return f'{self.left}.{self.right})'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.left, self.right

    def __eq__(self, other):
        if isinstance(other, Member):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self, parent=None, node=None):
        clone = Member(lineno=self.lineno, column=self.column)
        clone.left = self.left.clone(parent, clone)
        clone.right = self.right.clone(parent, clone)
        if clone.value:
            clone.value = self.value.clone(parent, clone)
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Member',
                           'left': self.left,
                           'right': self.right,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
