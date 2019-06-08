import json

from stilus.nodes.node import Node


class Supports(Node):

    def __init__(self, condition, lineno=1, column=1):
        super().__init__('supports', lineno=lineno, column=column)
        self.condition = condition
        self.block = None

    def __str__(self):
        return f'@supports {self.condition}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.condition

    def __eq__(self, other):
        if isinstance(other, Supports):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self, parent=None, node=None):
        clone = Supports(lineno=self.lineno, column=self.column)
        clone.condition = self.condition.clone(parent, clone)
        clone.block = self.block.clone(parent, clone)
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Supports',
                           'condition': self.condition,
                           'block': self.block,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
