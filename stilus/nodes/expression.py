import json

import utils
from nodes.boolean import Boolean
from nodes.node import Node


class Expression(Node):

    def __init__(self, is_list=False, preserve=False,
                 lineno=1, column=1):
        super().__init__(lineno=lineno, column=column)
        self.nodes = []
        self.is_list = is_list
        self.preserve = preserve

    def __str__(self):
        """
        :return: "(<a> <b> <c>)" or "(<a>, <b>, <c>)" if the expression
        represents a list.
        """
        separator = ' '
        if self.is_list:
            separator = ', '
        return '(' + separator.join(map(str, self.nodes)) + ')'

    def __repr__(self):
        return [n.__str__() for n in self.nodes]

    def __key(self):
        return self.nodes

    def __eq__(self, other):
        if isinstance(other, Expression):
            return self.__key() == other.__key()
        return False

    def __hash__(self):
        return id(self)

    def hash(self):
        hashes = [str(node.hash()) for node in self.nodes]
        return '::'.join(hashes)

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        return iter(self.nodes)

    def is_empty(self):
        return len(self.nodes) == 0

    def first(self):
        if not self.is_empty():
            return self.nodes[0].first()
        else:
            from nodes.null import null
            return null

    def clone(self, parent=None, node=None):
        clone = Expression(self.is_list,
                           lineno=self.lineno,
                           column=self.column)
        clone.preserve = self.preserve
        clone.filename = self.filename
        for something in self.nodes:
            clone.append(something.clone(parent, clone))
        return clone

    def to_boolean(self):
        if len(self.nodes) > 1:
            return Boolean(True)
        return self.first().to_boolean()

    def to_json(self):
        return json.dumps({'__type': 'Expression',
                           'isList': self.is_list,
                           'preserve': self.preserve,
                           'lineno': self.lineno,
                           'column': self.column,
                           'filename': self.filename,
                           'nodes': self.nodes})

    def operate(self, op, right, value=None):
        if op == '[]=':
            nodes = utils.unwrap(right).nodes
            value = utils.unwrap(value)
            for node in nodes:
                if node.node_name == 'unit':
                    index = utils.get_value(node)
                    last = len(self.nodes) - 1
                    for i in range(last, index):
                        from nodes.null import null
                        self.nodes.append(null)
                    self.nodes[index] = value
                elif node.string:
                    if not self.is_empty() and \
                            self.nodes[0].node_name == 'objectnode':
                        self.nodes[0].set(node.string, value.clone())
            return value
        elif op == '[]':
            expression = Expression()
            values = utils.unwrap(self).nodes
            nodes = utils.unwrap(right).nodes
            for node in nodes:
                n = None
                if node.node_name == 'unit':
                    index = utils.get_value(node)
                    try:
                        n = values[index]
                    except IndexError:
                        pass
                elif len(values) > 0 and values[0].node_name == 'objectnode':
                    n = values[0].get(node.string)
                if n:
                    expression.append(n)
            from nodes.null import null
            return null if expression.is_empty() else utils.unwrap(expression)
        elif op == '||':
            return self if self.to_boolean().value is True else right
        elif op == 'in':
            return super().operate(op, right, self.value)
        elif op == '!=':
            return self.operate('==', right, value).negate()
        elif op == '==':
            right = right.to_expression()
            if len(self.nodes) != len(right.nodes):
                return Boolean(False)
            for i in range(len(self.nodes)):
                a = self.nodes[i]
                b = right.nodes[i]
                if a.operate(op, b).is_true():
                    continue
                return Boolean(False)
            return Boolean(True)
        else:
            return self.first().operate(op, right, value)

    def append(self, node):
        self.nodes.append(node)
