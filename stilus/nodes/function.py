import copy
import json

from stilus.nodes.node import Node


class Function(Node):

    def __init__(self, function_name, params, body):
        super().__init__()
        self.function_name = function_name
        self.params = params
        self.fn = params
        self.body = body

    def __str__(self):
        return f'{self.function_name}({", ".join(self.params.nodes)})'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.function_name, self.params, self.body

    def __eq__(self, other):
        if isinstance(other, Function):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self):
        return copy.deepcopy(self)

    def arity(self):
        return len(self.params)

    def hash(self):
        return f'function {self.function_name}'

    def to_json(self):
        return json.dumps({'__type': 'Function',
                           'node_name': self.function_name,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename,
                           'params': self.params,
                           'block': self.block})
