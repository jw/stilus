import json

from stilus.nodes.node import Node


class Literal(Node):

    def __init__(self, string, css=False, prefixed=False, lineno=1, column=1):
        super().__init__(string, lineno=lineno, column=column)
        self.string = string
        self.css = css
        self.prefixed = prefixed

    def __str__(self):
        return f'{self.value}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.string, self.prefixed

    def __hash__(self):
        return hash(self.__key())

    # checkme: really no need - just call super()?
    def hash(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, Literal):
            return self.__key() == other.__key()
        return False

    def to_json(self):
        return json.dumps({'__type': 'Literal',
                           'val': self.value,
                           'string': self.string,
                           'prefixed': self.prefixed,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def coerce(self, other):
        if other.node_name in ['ident', 'string', 'literal']:
            return Literal(other.string)
        else:
            super().coerce(other)

    def operate(self, op, right):
        if op == "+":
            return Literal(self.string + self.coerce(right.first()).string)
        else:
            return super().operate(op, right)
