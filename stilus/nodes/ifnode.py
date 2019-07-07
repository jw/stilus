import json

from stilus.nodes.node import Node


class If(Node):

    def __init__(self, cond=None, negate=None, lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.cond = cond
        self.elses = []
        self.postfix = None
        self.block = None
        self.negate = None
        if negate:  # and isinstance(negate, bool):
            self.block = negate
        else:
            self.negate = negate

    def __str__(self):
        if self.elses:
            else_string = f' else ({", ".join(self.elses)})'
        else:
            else_string = ' [no else]'
        return f'if {self.cond}{else_string}'

    def __repr__(self):
        return self.__str__()

    def __key(self):
        return self.node_name, self.cond

    def __eq__(self, other):
        if isinstance(other, If):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return hash(self.__key())

    def clone(self, parent=None, node=None):
        clone = If()
        clone.cond = self.cond.clone(parent)
        clone.block = self.block.clone(parent, clone)
        clone.elses = [node.clone(parent, clone) for node in self.elses]
        clone.negate = self.negate
        clone.postfix = self.postfix
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps({'__type': 'If',
                           'cond': self.cond,
                           'block': self.block,
                           'elses': self.elses,
                           'negate': self.negate,
                           'postfix': self.postfix,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
