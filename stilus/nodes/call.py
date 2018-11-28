import copy
import json

from stilus.nodes.node import Node


class Call(Node):

    def __init__(self, function_name, args):
        super().__init__()
        self.function_name = function_name
        self.args = args

    def __str__(self):
        return f'{self.function_name}({", ".join(self.args)})'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.function_name, self.args

    def __eq__(self, other):
        if isinstance(other, Call):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Call',
                           'node_name': self.node_name,
                           'args': self.args,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
