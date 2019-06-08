import json

from stilus.nodes.node import Node


class Property(Node):

    def __init__(self, segments, expr=None, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.segments = segments
        self.expr = expr
        self.name = None
        self.literal = None

    def __str__(self):
        strings = [str(item) for item in self.segments]
        return f'property({"".join(strings)}, {self.expr})'

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

    def clone(self, parent=None, clone=None):
        clone = Property(self.segments)
        clone.name = self.name
        if self.literal:
            clone.literal = self.literal
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        clone.segments = [node.clone(parent, clone) for node in self.segments]
        if self.expr:
            clone.expr = self.expr.clone(parent, clone)
        return clone

    def to_json(self):
        # FIXME: add expr and literal to this dict
        return json.dumps({'__type': 'Property',
                           'segments': self.segments,
                           'name': self.name,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def operate(self, op, right, value):
        return self.expr.operate(op, right, value)
