import json

from stilus.nodes.node import Node


class Block(Node):

    def __init__(self, parent, node, scope=True, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.nodes = []
        self.parent = parent
        self.node = node
        self.scope = scope
        self.lacks_rendered_selectors = False  # for compiler
        self.index = 0
        self.mixin = False

    def __str__(self):
        return f'block [{self.lineno}:{self.column}] | scope: {self.scope}; ' \
               f'node: {self.node.node_name}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.nodes, self.node, self.parent, self.scope

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Block):
            return id(self) == id(other)
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
        if p is None:
            p = self.parent
        if n is None:
            n = self.node
        clone = Block(p, n, lineno=self.lineno, column=self.column)
        clone.filename = self.filename
        clone.scope = self.scope
        for something in self.nodes:
            clone.nodes.append(something.clone(clone, clone))
        return clone

    def append(self, node):
        self.nodes.append(node)

    def to_json(self):
        return json.dumps({'__type': 'Block',
                           'scope': self.scope,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename,
                           'nodes': self.nodes})
