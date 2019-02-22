import copy
import json

from stilus.nodes.expression import Expression


class Arguments(Expression):

    def __init__(self):
        super().__init__()
        self.map = []
        self.is_list = False

    def __str__(self):
        return str(self.map)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Arguments):
            return self.map == other.map
        return False

    def __hash__(self):
        return hash(self.map)

    @staticmethod
    def from_expression(expression: Expression):
        arguments = Arguments()
        arguments.lineno = expression.lineno
        arguments.column = expression.column
        arguments.is_list = expression.is_list
        for node in expression.nodes:
            arguments.append(node)
        return arguments

    def clone(self):
        return copy.deepcopy()

    def to_json(self):
        return json.dumps({'__type': 'Arguments',
                           'value': self.value,
                           'map': self.map,
                           'isList': self.is_list,
                           'preserve': self.preserve,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename,
                           'nodes': self.nodes})
