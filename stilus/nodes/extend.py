import json

from stilus.nodes.node import Node


class Extend(Node):

    def __init__(self, selectors, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.selectors = selectors
        self.optional = None

    def __str__(self):
        s = ', '.join(self.selectors)
        return f'@extend {s}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.selectors

    def __eq__(self, other):
        if isinstance(other, Extend):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self, parent=None, node=Node):
        clone = Extend(self.selectors,
                       lineno=self.lineno,
                       column=self.column)
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Charset',
                           'selectors': self.selectors,
                           'prefix': self.prefix,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
