import json
from typing import Type
from stilus.exceptions import StilusError


# todo: move this one to the stilus exceptions
class CoercionError(Exception):
    """CoercionError"""

    pass


current_filename = None  # todo: clean this up


class Node:
    """Node is the root class of all nodes."""

    def __init__(self, value=None, filename=None, lineno=1, column=1):
        self.value = value
        if not filename:
            self.filename = current_filename
        else:
            self.filename = filename
        self.lineno = lineno
        self.column = column
        self.node_name = self.__class__.__name__.lower()
        self.bubbled = False

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)

    def hash(self):
        """Return hash."""
        return self.value

    def first(self):
        """Return this node.
        :return: This node.
        """
        return self

    def to_boolean(self):
        """Return True.
        :return: True
        """
        from .boolean import Boolean

        return Boolean(True)

    def to_expression(self):
        """Return expression or wrap this node in an expression
        :return:
        """
        from stilus.nodes.expression import Expression

        if self.node_name == "expression":
            return self
        expression = Expression()
        expression.append(self)
        return expression

    def evaluate(self):
        """Nodes by default evaulate to themselves.
        :return: A Node.
        """
        from visitor.evaluator import Evaluator

        return Evaluator(self).evaluate()

    def one_is_unit(self, other):
        return self.node_name == "unit" or other.node_name == "unit"

    def operate(  # noqa: C901
        self, op: str, right: Type["Node"], value=None
    ) -> "Node":
        """Operate on ``right`` with the given ``op``."""
        from .boolean import Boolean

        if op == "is a":
            if "string" == right.first().node_name:
                return Boolean(self.node_name == right.value)
            else:
                raise Exception(
                    f'"is a" expects a string, ' f"got {right.toString}"
                )
        elif op == "==":
            from stilus import utils

            if utils.is_number(self) and utils.is_number(right):
                return Boolean(utils.get_value(self) == utils.get_value(right))
            return Boolean(self.hash() == right.hash())
        elif op == "!=":
            return Boolean(self.hash() != right.hash())
        elif op == ">=":
            return Boolean(self.hash() >= right.hash())
        elif op == "<=":
            return Boolean(self.hash() <= right.hash())
        elif op == ">":
            if self.one_is_unit(right):
                return Boolean(float(self.hash()) > float(right.hash()))
            return Boolean(self.hash() > right.hash())
        elif op == "<":
            return Boolean(self.hash() < right.hash())
        elif op == "||":
            return self if self.to_boolean().value is True else right
        elif op == "in":
            from stilus import utils

            values = utils.unwrap(right).nodes
            if not values:
                raise StilusError(
                    '"in" given invalid right-hand operand, '
                    "expecting an expression"
                )

            # 'prop' in object
            if len(values) == 1 and values[0].node_name == "objectnode":
                return Boolean(values[0].has(self.hash()))

            for value in values:
                if str(value.hash()) == str(self.hash()):
                    return Boolean(True)

            return Boolean(False)
        elif op == "&&":
            a = self.to_boolean()
            b = right.to_boolean()
            if a.value is True and b.value is True:
                return right
            elif a.value is False:
                return self
            return right
        elif op == "[]":
            raise StilusError(f"cannot perform {self}[{right}]")
        else:
            raise StilusError(f"cannot perform {self} {op} {right}")

    def should_coerce(self, op: str) -> bool:
        """Return False if `op` is generally not coerced."""
        if op in ["is a", "in", "||", "&&"]:
            return False
        return True

    def coerce(self, other: Type["Node"]) -> Type["Node"]:
        """Default coercion raises."""
        if other.node_name == self.node_name:
            return other
        raise CoercionError(f"cannot coerce {other} to {self.node_name}")

    def clone(self, parent=None, node=None):
        """Return this node."""
        return self

    def to_json(self):
        """Return a JSON representation of this node."""
        return json.dumps([self.lineno, self.column, self.filename])
