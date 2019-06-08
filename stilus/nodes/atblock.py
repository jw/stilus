import json

from stilus.nodes.node import Node


class Atblock(Node):

    def __init__(self, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
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

    def clone(self, parent=None, node=None):
        clone = Atblock()
        clone.block = self.block.clone(parent, clone)
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Atblock',
                           'block': self.block,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
