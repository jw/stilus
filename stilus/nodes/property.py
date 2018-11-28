import copy
import json

from stilus.nodes.node import Node


class Property(Node):

    def __init__(self, segments, expr=None):
        super().__init__()
        self.segments = segments
        self.expr = expr

    def __str__(self):
        return f'property({"".join(self.segments)}, {self.expr})'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.segments, self.expr

    def __eq__(self, other):
        if isinstance(other, Property):
            return self.__key() == other.__key()
        return False

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        # FIXME: add expr and literal to this dict
        return json.dumps({'__type': 'Property',
                           'segments': self.segments,
                           'node_name': self.node_name,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def operate(self, op, right, value):
        return self.expr.operate(op, right, value)
