import json

from stilus.nodes.node import Node


class Each(Node):

    def __init__(self, value, key, expr=None, block=None, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.value = value
        self.key = key
        self.expr = expr
        self.block = block

    def __str__(self):
        return f'{self.value}: {self.key} [{self.expr}] {self.block}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.value, self.key, self.expr, self.block

    def __eq__(self, other):
        if isinstance(other, Each):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self, parent=None, node=None):
        clone = Each(self.value, self.key)
        clone.expr = self.expr.clone(parent, clone)
        clone.block = self.block.clone(parent, clone)
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Each',
                           'val': self.value,
                           'key': self.key,
                           'expr': self.expr,
                           'block': self.block,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
