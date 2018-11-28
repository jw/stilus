import copy
import json

from stilus.nodes.node import Node


class Feature(Node):

    def __init__(self, segments):
        super().__init__()
        self.segments = segments
        self.expr = None

    def __str__(self):
        if self.expr:
            return f'({"".join(self.segments)}: {self.expr})'
        else:
            return ''.join(self.segments)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.segments, self.expr

    def __eq__(self, other):
        if isinstance(other, Feature):
            return self.__key() == other.__key()
        return False

    def clone(self):
        return copy.deepcopy(self)

    # todo: add expr and node_name
    def to_json(self):
        return json.dumps({'__type': 'Feature',
                           'segment': self.segments,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
