import copy
import json

from stilus.nodes.node import Node


class Literal(Node):

    def __init__(self, string, prefixed=''):
        super().__init__(string)
        self.string = string
        self.prefixed = prefixed

    def __str__(self):
        return f'{self.value}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.string, self.prefixed

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Literal):
            return self.__key() == other.__key()
        return False

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Literal',
                           'val': self.value,
                           'string': self.string,
                           'prefixed': self.prefixed,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def coerce(self, other):
        if other.name in ['ident', 'string', 'literal']:
            return Literal(other.string)
        else:
            super().coerce(other)

    def operate(self, op, right):
        if op == "+":
            return Literal(self.string + self.coerce(right.first()).string)
        else:
            return super().operate(op, right)
