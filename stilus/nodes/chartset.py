import json

from stilus.nodes.node import Node


class Charset(Node):

    def __init__(self, value, lineno=1, column=1):
        super().__init__(value, lineno=lineno, column=column)

    def __str__(self):
        return f'@charset {self.value}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.value

    def __eq__(self, other):
        if isinstance(other, Charset):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def to_json(self):
        return json.dumps({'__type': 'Charset',
                           'val': self.value,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
