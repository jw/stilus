import json

from stilus.nodes.node import Node


class Boolean(Node):

    def __init__(self, value: bool):
        super().__init__(bool(value))

    def __str__(self):
        return str(self.value).lower()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Boolean):
            return self.value == other.value
        return False

    def __hash__(self):
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


true = Boolean(True)
false = Boolean(False)
