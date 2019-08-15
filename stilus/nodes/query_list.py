import json

from stilus.nodes.node import Node


class QueryList(Node):

    def __init__(self, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.nodes = []

    def __str__(self):
        lst = []
        for node in self.nodes:
            lst.append(str(node))
        return f'({", ".join(lst)})'

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

    def clone(self, parent=None, node=None):
        clone = QueryList(lineno=self.lineno, column=self.column)
        clone.filename = self.filename
        clone.nodes = [node.clone(parent, clone) for node in self.nodes]
        return clone

    def to_json(self):
        return json.dumps({'__type': 'QueryList',
                           'nodes': self.nodes,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
