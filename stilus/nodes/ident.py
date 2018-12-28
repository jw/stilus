import copy
import json

from stilus.nodes.node import Node


class Ident(Node):

    def __init__(self, name, value=None, mixin=False):
        super().__init__(value)
        self.name = name
        self.string = name
        from stilus.nodes.null import null
        self.value = value if value else null
        self.mixin = mixin
        self.property = None

    def __str__(self):
        return f'{self.string}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.name, self.value, self.mixin

    def __eq__(self, other):
        if isinstance(other, Ident):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def hash(self):
        return self.name

    def clone(self):
        return copy.deepcopy(self)

    def is_empty(self):
        from stilus.nodes.null import null
        return self.value is null

    def to_json(self):
        return json.dumps({'__type': 'Ident',
                           'node_name': self.node_name,
                           'val': self.val,
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

    def operate(self, op, right):
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
