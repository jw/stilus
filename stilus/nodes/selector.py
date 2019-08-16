import json

from stilus.nodes.node import Node


class Selector(Node):

    def __init__(self, segments=None, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.inherits = True
        self.segments = segments
        self.optional = False
        self.block = None

    def __str__(self):
        try:
            string = ''.join(str(self.segments))
            if self.optional:
                string += ' !optional'
            return string
        except TypeError:
            return 'n/a'

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

    def clone(self, parent=None, node=None):
        clone = Selector(lineno=self.lineno, column=self.column)
        clone.filename = self.filename
        clone.inherits = self.inherits
        clone.value = self.value
        clone.segments = [node.clone(parent, clone) for node in self.segments]
        clone.optional = self.optional
        clone.block = self.block
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Selector',
                           'inherits': self.inherits,
                           'segments': self.segments,
                           'optional': self.optional,
                           'val': self.value,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
