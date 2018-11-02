import copy
import json

from stilus.nodes.node import Node


class Media(Node):

    def __init__(self, value):
        super().__init__(value)

    def __str__(self):
        return f'@media {self.value}'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, Media):
            return self.__key() == other.__key()
        return False

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Media',
                           'val': self.value,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
