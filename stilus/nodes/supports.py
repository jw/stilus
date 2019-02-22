import copy
import json

from stilus.nodes.node import Node


class Supports(Node):

    def __init__(self, condition):
        super().__init__('supports')
        self.condition = condition

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

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Supports',
                           'condition': self.condition,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
