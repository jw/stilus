import json

from stilus.nodes.expression import Expression


class Arguments(Expression):

    def __init__(self, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.map = {}
        self.is_list = False

    def __str__(self):
        return f''  # map: {self.map}'  # nodes: {self.nodes}'

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
        arguments = Arguments(lineno=expression.lineno,
                              column=expression.column)
        arguments.is_list = expression.is_list
        for node in expression.nodes:
            arguments.append(node)
        return arguments

    def clone(self, parent=None, node=None):
        clone = Arguments.from_expression(Expression.clone(self, parent))
        clone.is_list = self.is_list
        clone.map = {key: value.clone(parent, clone)
                     for (key, value) in self.map.items()}
        clone.is_list = self.is_list
        clone.filename = self.filename
        return clone

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
