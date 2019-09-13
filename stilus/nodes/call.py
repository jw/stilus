import json

from stilus.nodes.arguments import Arguments
from stilus.nodes.node import Node


class Call(Node):

    def __init__(self, function_name, args: Arguments = None,
                 lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.function_name = function_name
        self.block = None
        self.args = args

    def __str__(self):
        return f'{self.function_name}({", ".join(str(self.args))})'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.function_name, self.args

    def __eq__(self, other):
        if isinstance(other, Call):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.value)

    def clone(self, parent=None, clone=None):
        clone = Call(self.function_name)
        clone.args = self.args.clone(parent, clone)
        if self.block:
            clone.block = self.block.clone(parent, clone)
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Call',
                           'node_name': self.node_name,
                           'args': self.args,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
