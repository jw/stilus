import copy
import json

from stilus.nodes.node import Node


class Member(Node):

    def __init__(self, left, right):
        super().__init__()
        self.right = right
        self.left = left

    def __str__(self):
        return f'{self.left}.{self.right})'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.name, self.left, self.right

    def __eq__(self, other):
        if isinstance(other, Member):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Member',
                           'left': self.left,
                           'right': self.right,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
