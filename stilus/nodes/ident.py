import json

from stilus.nodes.node import Node


class Ident(Node):

    def __init__(self, name, value=None, mixin=False,
                 lineno=1, column=1):
        super().__init__(value, lineno=lineno, column=column)
        self.name = name
        self.string = name
        # todo: clean this up
        from stilus.nodes.null import null
        self.value = null if value is None else value
        self.mixin = mixin
        self.property = None
        self.rest = False

    def __str__(self):
        return f'{self.string}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.name, self.value, self.mixin, self.property, \
               self.lineno, self.column

    def __eq__(self, other):
        if isinstance(other, Ident):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.name)

    def hash(self):
        return self.name

    def clone(self, parent=None, node=None):
        clone = Ident(self.name)
        clone.value = self.value.clone(parent, clone)
        clone.mixin = self.mixin
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        clone.property = self.property
        clone.rest = self.rest
        return clone

    def is_empty(self):
        from stilus.nodes.null import null
        return self.value is null

    def to_json(self):
        return json.dumps({'__type': 'Ident',
                           'node_name': self.node_name,
                           'val': self.value,
                           'mixin': self.mixin,
                           'property': self.property,
                           'rest': self.rest,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def coerce(self, other):
        if other.node_name in ['ident', 'string', 'literal']:
            return Ident(other.string)
        elif other.node_name == 'unit':
            return Ident(other.__str__())
        else:
            return super().coerce(other)

    def operate(self, op, right, value=None):
        value = right.first()
        if op == '-':
            if value.name == 'unit':
                from stilus.nodes.expression import Expression
                expression = Expression()
                value = value.clone()
                value.value = -value.value
                expression.push(self)
                expression.push(value)
                return expression
        elif op == "+":
            return Ident(self.string + self.coerce(value).string)
        return super().operate(op, right)
