import copy
import json

from stilus.nodes.node import Node


class QueryList(Node):

    def __init__(self):
        super().__init__()
        self.nodes = []

    def __str__(self):
        return '(' + ', '.join(self.nodes) + ')'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.nodes

    def __eq__(self, other):
        if isinstance(other, QueryList):
            return self.__key() == other.__key()
        return False

    def merge(self, other):
        list = QueryList()
        for i, query in enumerate(self.nodes):
            merged = query.merge(other.nodes[i])
            if merged:
                list.append(merged)
        return list

    def append(self, node):
        self.nodes.append(node)

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'QueryList',
                           'nodes': self.nodes,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
