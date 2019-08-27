import json

from stilus.nodes.block import Block
from stilus.nodes.node import Node
from stilus.nodes.selector import Selector


class Group(Node):

    def __init__(self, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.nodes = []
        self.extends = []

    def __str__(self):
        return f'{self.nodes}:{self.extends}'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def append(self, selector: Selector):
        self.nodes.append(selector)

    @property
    def block(self):
        if self.nodes[0]:
            return self.nodes[0].block
        else:
            return None

    @block.setter
    def block(self, block: Block):
        for node in self.nodes:
            node.block = block

    def has_only_placeholders(self):
        return all(s.is_placeholder() for s in self.nodes)

    def clone(self, parent=None, noe=None):
        clone = Group(lineno=self.lineno, column=self.column)
        clone.filename = self.filename
        clone.nodes = [node.clone(parent, clone) for node in self.nodes]
        clone.block = self.block.clone(parent, clone)
        return clone

    def to_json(self):
        return json.dumps({'__type': 'Group',
                           'nodes': self.nodes,
                           'block': self.block,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
