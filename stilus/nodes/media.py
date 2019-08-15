import json

from stilus.nodes.atrule import Atrule


class Media(Atrule):

    def __init__(self, value=None, lineno=1, column=1):
        super().__init__('media', lineno=lineno, column=column)
        self.value = value

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

    def clone(self, parent=None, noe=None):
        clone = Media(lineno=self.lineno, column=self.column)
        clone.value = self.value.clone(parent, clone)
        clone.block = self.block.clone(parent, clone)
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Media',
                           'val': self.value,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
