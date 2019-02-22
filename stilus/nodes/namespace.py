import copy
import json

from stilus.nodes.node import Node


class Namespace(Node):

    def __init__(self, value, prefix=None):
        super().__init__(value)
        self.prefix = prefix

    def __str__(self):
        prefix = f'{self.prefix} ' if self.prefix else ''
        return f'@namespace {prefix}{self.value}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.value, self.prefix

    def __eq__(self, other):
        if isinstance(other, Namespace):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Charset',
                           'val': self.value,
                           'prefix': self.prefix,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
