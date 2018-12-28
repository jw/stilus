import copy
import json
from collections import deque

from deprecated import deprecated

from stilus.nodes.node import Node


class Root(Node):

    def __init__(self):
        super().__init__()
        self.nodes = deque([])

    @deprecated(reason='use append')
    def push(self, node):
        self.nodes.append(node)

    def append(self, node):
        self.nodes.append(node)

    def unshift(self, node):
        self.nodes.appendleft(node)

    def clone(self):
        return copy.deepcopy(self)

    def __key(self):
        return self.nodes

    def __eq__(self, other):
        if isinstance(other, Root):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return f'[Root]'

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return json.dumps({'__type': 'Root',
                           'nodes': self.nodes,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
