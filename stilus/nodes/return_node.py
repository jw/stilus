import json

from stilus.nodes.expression import Expression
from stilus.nodes.node import Node


class ReturnNode(Node, Exception):

    def __init__(self, expression: Expression = None, lineno=1, column=1):
        Node.__init__(self, lineno=lineno, column=column)
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

    def clone(self, parent=None, node=None):
        clone = ReturnNode(lineno=self.lineno, column=self.column)
        clone.filename = self.filename
        clone.expression = self.expression.clone(parent, clone)
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Return',
                           'expr': self.expression,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
