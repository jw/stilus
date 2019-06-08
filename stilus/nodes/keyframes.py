import json

from stilus.nodes.atrule import Atrule


class Keyframes(Atrule):

    def __init__(self, segments, prefix='official', lineno=1, column=1):
        super().__init__('keyframes', lineno=lineno, column=column)
        self.segments = segments
        if prefix:
            self.prefix = prefix
        else:
            self.prefix = 'official'
        self.frames = None
        self.fabricated = False
        self.block = None

    def __str__(self):
        return f'@keyframes {"".join(self.segments)}'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.segments, self.prefix

    def __eq__(self, other):
        if isinstance(other, Keyframes):
            return self.__key() == other.__key()
        return False

    def clone(self, parent=None, node=None):
        clone = Keyframes([], lineno=self.lineno, column=self.column)
        clone.filename = self.filename
        clone.segments = [segment for segment in self.segments]
        clone.prefix = self.prefix
        clone.block = self.block.clone(parent, clone)
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Keyframes',
                           'segments': self.segments,
                           'prefix': self.prefix,
                           'block': self.block,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
