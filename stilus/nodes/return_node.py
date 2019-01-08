import copy
import json

from nodes.expression import Expression
from stilus.nodes.node import Node


class ReturnNode(Node):

    def __init__(self, expression: Expression = None):
        super().__init__()
        self.expression = expression

    def __str__(self):
        return f'Return[{self.expression}]'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.type, self.expression

    def __eq__(self, other):
        if isinstance(other, ReturnNode):
            return self.__key() == other.__key()
        return False

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Return',
                           'expr': self.expression,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
