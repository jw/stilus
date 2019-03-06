import copy
import json

from stilus.nodes.node import Node


class Atrule(Node):

    def __init__(self, type):
        super().__init__()
        self.type = type
        self.block = None
        self.segments = None

    def __str__(self):
        return f'@{self.type}'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, Atrule):
            return self.__key() == other.__key()
        return False

    def has_output(self):
        return self.block and self._has_output(self.block)

    def _has_output(self, block):
        # only placeholder selectors
        if hasattr(block, 'nodes') and \
                all(node.node_name == 'group' and node.has_only_placeholders()
                    for node in block.nodes):
            return False

        # something visible
        return hasattr(block, 'nodes') and \
            any(node.node_name in ['property', 'literal', 'import'] or
                self._has_output(node) or
                self._has_output(node.block)
                for node in block.nodes)

    def has_only_properties(self):
        if not self.block:
            return False
        for node in self.block.nodes:
            if node.name in ['property', 'expression', 'comment']:
                continue
            else:
                return False
        return True

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Atrule',
                           'type': self.type,
                           'segments': self.segments,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
