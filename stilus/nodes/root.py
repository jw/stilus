import json

from stilus.nodes.node import Node


class Root(Node):

    def __init__(self, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.nodes = []

    def append(self, node):
        self.nodes.append(node)

    def unshift(self, node):
        self.nodes.insert(0, node)

    def __key(self):
        return self.nodes

    def __eq__(self, other):
        if isinstance(other, Root):
            return id(self) == id(other)
        return False

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return f'[Root]'

    def __repr__(self):
        return self.__str__()

    def clone(self, parent=None, node=None):
        clone = Root(lineno=self.lineno, column=self.column)
        clone.filename = self.filename
        clone.nodes = [node.clone(clone, clone) for node in self.nodes]
        return clone

    def to_json(self):
        return json.dumps(self.__dict__)
        # return json.dumps({'__type': 'Root',
        #                    'nodes': self.nodes,
        #                    'lineno': self.lineno,
        #                    'column': self.column,
        #                    'filename': self.filename})
