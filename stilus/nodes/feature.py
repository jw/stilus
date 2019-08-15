import json

from stilus.nodes.node import Node


class Feature(Node):

    def __init__(self, segments=None, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.segments = segments
        self.expr = None
        self.name = None

    def __str__(self):
        if self.expr:
            s = ''
            for segment in self.segments:
                s += str(segment)
            return f'({s}: {self.expr})'
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

    def clone(self, parent=None, node=None):
        clone = Feature(lineno=self.lineno, column=self.column)
        clone.segments = [node.clone(parent, clone) for node in self.segments]
        if self.expr:
            clone.expr = self.expr.clone(parent, clone)
        clone.name = self.name
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Feature',
                           'segment': self.segments,
                           'expr': self.expr,
                           'name': self.name,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
