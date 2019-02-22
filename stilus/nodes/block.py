import json

from deprecated import deprecated

from stilus.nodes.node import Node


class Block(Node):

    def __init__(self, parent, node, scope=True):
        super().__init__()
        self.nodes = []
        self.parent = parent
        self.node = node
        self.scope = scope
        self.lacks_rendered_selectors = False  # for compiler

    def __str__(self):
        return f'{self.parent}:{self.node}:{self.nodes}:{self.scope}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.nodes, self.node, self.parent, self.scope

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Block):
            return self.__key() == other.__key()
        return False

    def has_properties(self):
        for node in self.nodes:
            if node.node_name == 'property':
                return True
        return False

    def has_media(self):
        for node in self.nodes:
            if node.node_name == 'media':
                return True
        return False

    def __len__(self):
        return len(self.nodes)

    def is_empty(self):
        return len(self.nodes) == 0

    def clone(self, parent=None, node=None):
        p = parent
        n = node
        if not p:
            p = self.parent
        if not n:
            n = self.node
        clone = Block(p, n)
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        clone.scope = self.scope
        for node in self.nodes:
            clone.append(node.clone())
        return clone

    @deprecated(reason='use append')
    def push(self, node):
        self.nodes.append(node)

    def append(self, node):
        self.nodes.append(node)

    def to_json(self):
        return json.dumps({'__type': 'Block',
                           'scope': self.scope,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename,
                           'nodes': self.nodes})
