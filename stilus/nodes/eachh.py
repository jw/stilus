import copy
import json

from stilus.nodes.node import Node


class Eachh(Node):

    def __init__(self, value, key, expression, block):
        super().__init__(value)
        self.key = key
        self.expression = expression
        self.block = block

    def __str__(self):
        return f'each({self.value}, {self.key}, ' \
               f'{self.expression}, {self.block})'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.value, self.key, self.expression, self.block

    def __eq__(self, other):
        if isinstance(other, Eachh):
            return self.__key() == other.__key()
        return False

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Each',
                           'val': self.value,
                           'key': self.key,
                           'expr': self.expression,
                           'block': self.block,
                           'postfix': self.postfix,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
