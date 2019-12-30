import json

from stilus import utils
from .boolean import Boolean
from .expression import Expression
from .node import Node


class String(Node):
    def __init__(self, value, quote=None, lineno=1, column=1):
        super().__init__(value, lineno=lineno, column=column)
        self.string = value
        self.prefixed = False
        if not isinstance(quote, str):
            self.quote = "'"
        else:
            self.quote = quote

    def __str__(self):
        return f"{self.quote}{self.value}{self.quote}"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(str(self))

    def clone(self, parent=None, node=None):
        clone = String(
            self.value, self.quote, lineno=self.lineno, column=self.column
        )
        clone.filename = self.filename
        return clone

    def to_json(self):
        return json.dumps(
            {
                "__type": "Boolean",
                "value": self.value,
                "quote": self.quote,
                "lineno": self.lineno,
                "column": self.column,
                "filename": self.filename,
            }
        )

    def to_boolean(self):
        return Boolean(len(self.value))

    def coerce(self, other: Node):
        if other.node_name == "string":
            return other
        elif other.node_name == "expression":
            node_values = [self.coerce(node).value for node in other.nodes]
            return String(" ".join(node_values))
        else:
            return String(other.__str__())

    def operate(self, op, right, value=None):
        if op == "%":
            expr = Expression()
            expr.append(self)
            # constructor args
            if right.node_name == "expression":
                args = utils.unwrap(right)
            else:
                args = [right]
            # apply
            from stilus.functions.s import s

            if hasattr(args, "nodes"):
                return s(expr, *args.nodes)
            else:
                return s(expr, args[0])
        if op == "+":
            expr = Expression()
            expr.append(
                String(
                    self.value + self.coerce(right).value,
                    lineno=self.lineno,
                    column=self.column,
                )
            )
            return expr
        else:
            return super().operate(op, right)
