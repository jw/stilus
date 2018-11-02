import copy
import json

from stilus.nodes.block import Block
from stilus.nodes.node import Node
from stilus.nodes.selector import Selector


class Group(Node):

    def __init__(self):
        super().__init__()
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

    def push(self, selector: Selector):
        self.nodes.append(selector)

    # TODO: getter?
    def get_block(self):
        if self.nodes[0]:
            return self.nodes[0].block
        else:
            return None

    # TODO: setter?
    def set_block(self, block: Block):
        for node in self.nodes:
            node.block = block

    def has_only_placeholders(self):
        return all(s.is_placeholder() for s in self.nodes)

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Group',
                           'nodes': self.nodes,
                           'block': self.block,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
