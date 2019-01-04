import copy
import json

from stilus.nodes.node import Node


class Atblock(Node):

    def __init__(self):
        super().__init__()
        self.block = None

    def __str__(self):
        return f'@block'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.block

    def __eq__(self, other):
        if isinstance(other, Atblock):
            return self.__key() == other.__key()
        return False

    def nodes(self):
        if self.block:
            return self.block.nodes
        else:
            return []

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Atblock',
                           'block': self.block,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
