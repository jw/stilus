import copy
import json

from stilus.nodes.node import Node


class Params(Node):

    def __init__(self):
        super().__init__()
        self.nodes = []

    def __str__(self):
        return f'nothing'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name

    def __eq__(self, other):
        if isinstance(other, Params):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def __len__(self):
        return len(self.nodes)

    def append(self, node):
        self.nodes.append(node)

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Params',
                           'nodes': self.nodes,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
