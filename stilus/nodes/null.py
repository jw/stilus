import json

from stilus.nodes.node import Node


class Null(Node):

    def __init__(self):
        super().__init__()
        self.lineno = 0
        self.column = 0

    def is_null(self):
        return True

    def __str__(self):
        return 'null'

    def __repr__(self):
        return str(self)

    def __bool__(self):
        return False

    def __eq__(self, other):
        if isinstance(other, Null):
            return True
        return False

    def __hash__(self):
        return hash(None)

    def hash(self):
        return None

    def clone(self, parent=None, node=None):
        return self

    def to_boolean(self):
        from stilus.nodes.boolean import false
        return false

    def to_json(self):
        return json.dumps({'__type': 'Null',
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})


null = Null()
