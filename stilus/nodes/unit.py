import copy
import json
from math import isnan

from stilus.nodes.boolean import true, Boolean
from stilus.nodes.expression import Expression
from stilus.nodes.node import Node

FACTOR_TABLE = {'mm': {'value': 1, 'label': 'mm'},
                'cm': {'value': 10, 'label': 'mm'},
                'in': {'value': 25.4, 'label': 'mm'},
                'pt': {'value': 25.4 / 72, 'label': 'mm'},
                'ms': {'value': 1, 'label': 'ms'},
                's': {'value': 1000, 'label': 'ms'},
                'Hz': {'value': 1, 'label': 'Hz'},
                'kHz': {'value': 1000, 'label': 'Hz'}}


class Unit(Node):

    def __init__(self, value, type=None):
        super().__init__(value)
        self.type = type

    def __str__(self):
        type = self.type if self.type else ''
        return f'{self.value}{type}'

    def __repr__(self):
        return self.__str__()

    def to_boolean(self):
        return true if self.type else Boolean(self.value)

    def to_json(self):
        return json.dumps({'__type': 'Unit',
                           'value': self.value,
                           'type': self.type,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})

    def clone(self):
        return copy.deepcopy(self)

    def operate(self, op, right: Node):
        type = self.type if self.type else right.first().type

        # swap color
        if right.name in ['rgba', 'hsla']:
            return right.operate(op, self)

        # operate
        if self.should_coerce(op):
            right = right.first()

            if self.type != '%' and op in ['-', '+'] and self.type == '%':
                right = Unit(self.value * (right.value / 100), '%')
            else:
                right = self.coerce(right)

            if op == '-':
                return Unit(self.value - right.value, type)
            elif op == '+':
                # keyframes interpolation
                if self.type:
                    type = type
                else:
                    type = right.type == '%' and right.type
                return Unit(self.value + right.value, type)
            elif op == '/':
                return Unit(self.value / right.value, type)
            elif op == '*':
                return Unit(self.value * right.value, type)
            elif op == '%':
                return Unit(self.value % right.value, type)
            elif op == '**':
                return Unit(self.value ** right.value, type)
            elif op in ['..', '...']:
                start = self.value
                end = right.value
                expr = Expression()
                inclusive = '..' == op
                if start < end:
                    while True:
                        expr.push(Unit(start))
                        if ++start <= end if inclusive else ++start < end:
                            break
                else:
                    while True:
                        expr.push(Unit(start))
                        if --start >= end if inclusive else --start > end:
                            break
                return expr

        return super().operate(op, right)

    def coerce(self, other):
        if other.name == 'unit':
            a = self
            b = other
            factor_a = FACTOR_TABLE[a.type]
            factor_b = FACTOR_TABLE[b.type]

            if factor_a and factor_b and factor_a.label == factor_b.label:
                b_value = b.value * (factor_b.value / factor_a.value)
                return Unit(b_value, a.type)
            else:
                return Unit(b.value, a.type)
        elif other.name == 'string':
            # keyframes interpretation
            if other.value == '%':
                return Unit(0, '%')
            value = float(other.value)
            if isnan(value):
                return super().coerce(self, value)
            else:
                return Unit(value)
        else:
            return super().coerce(self, other)
