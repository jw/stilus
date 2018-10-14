import copy
import json


class CoercionError(Exception):
    pass


class Node:

    def __init__(self, value=None, filename=None, lineno=1, column=1):
        self.value = value
        self.filename = filename
        self.lineno = lineno
        self.column = column
        self.name = self.__class__.__name__.lower()

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)

    def first(self):
        return self

    def to_json(self):
        return json.dumps([self.lineno, self.column, self.filename])

    def to_boolean(self):
        return True

    def to_expression(self):
        from stilus.nodes.expression import Expression
        if self.name == 'expression':
            return self
        expression = Expression()
        expression.push(self)
        return expression

    def evaluate(self):
        from stilus.evaluator import Evaluator
        return Evaluator(self).evaluate()

    def operate(self, op, right):
        from stilus.nodes.boolean import Boolean
        if op == 'is a':
            if 'string' == right.first().name:
                return Boolean(self.name == right.value)
            else:
                raise Exception(f'"is a" expects a string, '
                                f'got {right.toString}')
        elif op == '==':
            return Boolean(hash(self) == hash(right))
        elif op == '!=':
            return Boolean(hash(self) != hash(right))
        elif op == '>=':
            return Boolean(hash(self) >= hash(right))
        elif op == '<=':
            return Boolean(hash(self) <= hash(right))
        elif op == '>':
            return Boolean(hash(self) > hash(right))
        elif op == '<':
            return Boolean(hash(self) < hash(right))
        elif op == '||':
            return self if self.toBoolean().isTrue else right
        elif op == 'in':
            from stilus import utils
            values = utils.unwrap(right)
            if not values:
                raise Exception('"in" given invalid right-hand operand, '
                                'expecting an expression')
            if len(values) == 1:
                return Boolean(values[0].has(self.hash))

            for value in values:
                if value.hash == self.hash:
                    return Boolean(True)

            return Boolean(False)
        elif op == '&&':
            a = self.to_boolean()
            b = right.to_boolean()
            if a and b:
                return right
            elif a:
                return self
            return right
        elif op == '[]':
            raise Exception(f'cannot perform {self}[{right}]')
        else:
            raise Exception(f'cannot perform {self} {op} {right}')

    def clone(self):
        return copy.deepcopy(self)

    def should_coerce(self, op):
        if op in ['is a', 'in', '||', '&&']:
            return False
        return True

    def coerce(self, other):
        if other.name == self.name:
            return other
        raise CoercionError(f'cannot coerce {other} to {self.name}')
