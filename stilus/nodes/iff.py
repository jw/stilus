import copy
import json

from stilus.nodes.node import Node


class Iff(Node):

    def __init__(self, cond, negate=None):
        super().__init__()
        self.cond = cond
        self.elses = []
        self.block = None
        self.negate = None
        if negate and negate.name:
            self.block = negate
        else:
            self.negate = negate

    def __str__(self):
        return f'if({self.cond}, {self.negate})'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.cond, self.negate

    def __eq__(self, other):
        if isinstance(other, Iff):
            return self.__key() == other.__key()
        return False

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'If',
                           'cond': self.cond,
                           'block': self.block,
                           'elses': self.elses,
                           'negate': self.negate,
                           'postfix': self.postfix,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
