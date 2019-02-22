import copy
import json

from stilus.nodes.atrule import Atrule


class Keyframes(Atrule):

    def __init__(self, segments, prefix=None):
        super().__init__('keyframes')
        self.segments = segments
        self.prefix = prefix
        self.frames = []
        self.fabricated = False

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

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Keyframes',
                           'segments': self.segments,
                           'prefix': self.prefix,
                           'block': self.block,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
