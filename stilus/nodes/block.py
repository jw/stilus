import copy
import json

from stilus.nodes.node import Node


class Block(Node):

    def __init__(self, parent, node):
        super().__init__()
        self.nodes = []
        self.parent = parent
        self.node = node
        self.scope = True

    def __str__(self):
        return f'{self.parent}:{self.node}:{self.nodes}:{self.scope}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.nodes, self.node, self.parent, self.scope

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Block):
            return self.__key() == other.__key()
        return False

    def has_properties(self):
        for node in self.nodes:
            if node.name == 'property':
                return True
        return False

    def has_media(self):
        for node in self.nodes:
            if node.name == 'media':
                return True
        return False

    def __len__(self):
        return len(self.nodes)

    def is_empty(self):
        return len(self.nodes) == 0

    def clone(self):
        return copy.deepcopy(self)

    def push(self, node):
        self.nodes.append(node)

    def to_json(self):
        return json.dumps({'__type': 'Block',
                           'scope': self.scope,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename,
                           'nodes': self.nodes})
