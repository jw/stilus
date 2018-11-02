import copy
import json

from stilus.nodes.node import Node


class Selector(Node):

    def __init__(self, segments):
        super().__init__()
        self.inherits = True
        self.segments = segments
        self.optional = False
        self.block = None  # FIXME: should this be here?

    def __str__(self):
        string = ''.join(self.segments)
        if self.optional:
            string += ' !optional'
        return string

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.inherits, self.segments, self.optional

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def is_placeholder(self):
        if self.value and '$' in self.value[0:1]:
            return True
        else:
            return False

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Selector',
                           'inherits': self.inherits,
                           'segments': self.segments,
                           'optional': self.optional,
                           'val': self.value,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
