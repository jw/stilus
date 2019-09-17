import json

from stilus.functions.bifs import bifs
from stilus.nodes.node import Node


class Function(Node):

    def __init__(self, function_name, params=None, body=None,
                 lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.function_name = function_name
        self.params = params
        self.builtin = self.function_name in bifs.keys()
        self.block = body
        self.fn = None
        if hasattr(params, '__call___'):
            self.fn = params
        # else:
        #     self.fn = None

    def __str__(self):
        if self.params:
            if hasattr(self.params, 'nodes'):
                strings = [str(node if node else 'None')
                           for node in self.params.nodes]
                return f'{self.function_name}({", ".join(strings)})'
            else:
                return f'{self.function_name}()'
        else:
            return f'{self.function_name}()'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.function_name, self.params, self.block

    def __eq__(self, other):
        if isinstance(other, Function):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def hash(self):
        return f'function {self.function_name}'

    def clone(self, parent=None, node=None):
        if self.fn:
            # check this: what is fn?
            clone = Function(self.function_name, self.fn)
        else:
            clone = Function(self.function_name)
            if hasattr(self.params, 'clone'):
                clone.params = self.params.clone(parent, clone)
            if hasattr(self.block, 'clone'):
                clone.block = self.block.clone(parent, clone)
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        return clone

    def arity(self):
        return len(self.params)

    def to_json(self):
        return json.dumps({'__type': 'Function',
                           'node_name': self.function_name,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename,
                           'params': self.params,
                           'block': self.block})
