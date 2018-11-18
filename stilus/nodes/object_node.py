import copy
import json

from stilus.nodes.boolean import false, true, Boolean
from stilus.nodes.node import Node
from stilus.nodes.null import null


class ObjectNode(Node):

    def __init__(self, values: dict):
        super().__init__()
        self.values = values

    def __str__(self):
        obj = {}
        for key, value in self.values.items():
            obj[str(key)] = str(value)
        return json.dumps(obj)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return self.values

    def __eq__(self, other):
        if isinstance(other, ObjectNode):
            return self.__key() == other.__key()
        return False

    def set(self, key, val):
        self.values[key] = val
        return self

    def get(self, key):
        return self.value.get(key, null)

    def __len__(self):
        return len(self.values)

    def __contains__(self, key):
        return key in self.values

    def operate(self, op, right):
        if op in ['.', '[]']:
            return self.get(right.hash())
        elif op == '==':
            values = self.values
            if right.name != 'object' or len(self) != len(right):
                return false
            for key in values:
                a = values[key]
                b = right.values[key]
                if a.operate(op, b).is_false:
                    return false
                    return true
        elif op == '!=':
            return self.operate('==', right).negate()
        else:
            return self.operate(op, right)

    def to_boolean(self):
        return Boolean(len(self))

    def to_block(self):

        # fixme: node.nodes
        def to_string(node):
            if node.nodes:
                return str(node.nodes)
            else:
                return '\\,'
            return str(node)

        string = '{'
        for key, value in self.values.items():
            if value.first.name == 'object':
                string += key + ' ' + value.first.to_block()
            else:
                if key == '@charset':
                    string += key + ' ' + str(value.first) + ';'
                else:

                    string += key + ':' + to_string(value) + ';'
        string += '}'
        return string

    def clone(self):
        return copy.deepcopy(self)

    def to_json(self):
        return json.dumps({'__type': 'Object',
                           'vals': self.values,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename})
