import copy
import json

from stilus.nodes.node import Node


class Import(Node):

    def __init__(self, expr, once=False):
        super().__init__()
        self.path = expr
        self.once = once
        self.mtime = None

    def __str__(self):
        return f'import({self.path}, {self.once}'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.path, self.once

    def __eq__(self, other):
        if isinstance(other, Import):
            return self.__key() == other.__key()
        return False

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Import',
                           'path': self.path,
                           'once': self.once,
                           'mtime': self.mtime,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
