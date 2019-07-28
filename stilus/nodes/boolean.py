import json

from stilus.nodes.node import Node


class Boolean(Node):

    def __init__(self, value: bool, lineno=1, column=1):
        from stilus.nodes.null import null
        if value == null:
            value = False
        super().__init__(bool(value), lineno=lineno, column=column)

    def __str__(self):
        return str(self.value).lower()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Boolean):
            return self.value == other.value
        return False

    def __hash__(self):
        # todo: fix this!
        return hash(self.value)

    def is_true(self):
        return self.value is True

    def is_false(self):
        return self.value is False

    def negate(self):
        self.value = not self.value
        return self

    def to_json(self):
        return json.dumps({'__type': 'Boolean', 'value': self.value})

    def to_boolean(self):
        return self


true = Boolean(True)
false = Boolean(False)
