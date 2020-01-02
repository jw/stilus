import json

from .boolean import Boolean
from .expression import Expression
from .node import Node

FACTOR_TABLE = {
    "mm": {"value": 1, "label": "mm"},
    "cm": {"value": 10, "label": "mm"},
    "in": {"value": 25.4, "label": "mm"},
    "pt": {"value": 25.4 / 72, "label": "mm"},
    "ms": {"value": 1, "label": "ms"},
    "s": {"value": 1000, "label": "ms"},
    "Hz": {"value": 1, "label": "Hz"},
    "kHz": {"value": 1000, "label": "Hz"},
}


# todo: remove this function!
def is_weird_float(value):
    if isinstance(value, float) and f"{value}".endswith(".0"):
        return True
    return False


def has_many_zeros_and_a_number(value):
    if isinstance(value, (float, str)):
        s = f"{value}"
        if "." in s and len(s.split(".")[1]) > 10 and s[-1].isdigit():
            return True
    return False


class Unit(Node):
    def __init__(self, value, type=None, lineno=1, column=1):
        """
        Initialize a new `Unit` with the given `val` and unit `type` such as
        "px", "pt", "in", etc.
        :param value:
        :param type:
        """
        super().__init__(value, lineno=lineno, column=column)
        self.type = type

    def __str__(self):
        type = self.type if self.type else ""
        # remove trailing zeros
        if is_weird_float(self.value):  # fixme: do not use this!
            v = f"{self.value}".rstrip("0").rstrip(".")
        elif has_many_zeros_and_a_number(self.value):  # fixme: remove this!
            v = f"{self.value[:-1]}".rstrip("0")
        else:
            v = self.value
        return f"{v}{type}"

    def __repr__(self):
        return self.__str__()

    def to_boolean(self):
        return Boolean(True) if self.type else Boolean(self.value)

    def to_json(self):
        return json.dumps(
            {
                "__type": "Unit",
                "value": self.value,
                "type": self.type,
                "lineno": self.lineno,
                "column": self.column,
                "filename": self.filename,
            }
        )

    def clone(self, parent=None, node=None):
        clone = Unit(self.value, self.type)
        clone.lineno = self.lineno
        clone.column = self.column
        clone.filename = self.filename
        return clone

    def hash(self):
        if isinstance(self.value, int) or is_weird_float(self.value):  # fixme!
            return int(self.value)
        else:
            return self.value

    def operate(self, op, right: Node, value=None):  # noqa: C901
        type = None
        if self.type:
            type = self.type
        elif hasattr(right.first(), "type") and right.first().type:
            type = right.first().type

        # swap color
        if right.node_name in ["rgba", "hsla"]:
            return right.operate(op, self)

        # operate
        if self.should_coerce(op):
            right = right.first()

            if (
                hasattr(self, "type")
                and self.type != "%"
                and op in ["-", "+"]
                and hasattr(right, "type")
                and right.type == "%"
            ):
                right = Unit(self.value * (right.value / 100), "%")
            else:
                right = self.coerce(right)

            if op == "-":
                return Unit(self.value - right.value, type)
            elif op == "+":
                # keyframes interpolation
                if type:
                    type = type
                else:
                    type = right.type if right.type == "%" else None
                return Unit(self.value + right.value, type)
            elif op == "/":
                return Unit(self.value / right.value, type)
            elif op == "*":
                return Unit(self.value * right.value, type)
            elif op == "%":
                return Unit(self.value % right.value, type)
            elif op == "**":
                return Unit(self.value ** right.value, type)
            elif op in ["..", "..."]:
                start = int(self.value)
                end = int(right.value)
                expr = Expression()
                inclusive = ".." == op
                if start < end:
                    while True:
                        expr.append(Unit(start))
                        start += 1
                        if inclusive and start > end:
                            break
                        if not inclusive and start >= end:
                            break
                else:
                    while True:
                        expr.append(Unit(start))
                        start -= 1
                        if inclusive and start < end:
                            break
                        if not inclusive and start <= end:
                            break
                return expr

        return super().operate(op, right)

    def coerce(self, other):
        if other.node_name == "unit":
            a = self
            b = other

            if a.type:
                factor_a = FACTOR_TABLE.get(
                    a.type, {"value": 1, "label": a.type}
                )
            else:
                factor_a = None
            if b.type:
                factor_b = FACTOR_TABLE.get(
                    b.type, {"value": 1, "label": b.type}
                )
            else:
                factor_b = None

            if (
                factor_a
                and factor_b
                and factor_a["label"] == factor_b["label"]
            ):
                b_value = b.value * (factor_b["value"] / factor_a["value"])
                return Unit(b_value, a.type)
            else:
                return Unit(b.value, a.type)
        elif other.node_name == "string":
            # keyframes interpretation
            if other.value == "%":
                return Unit(0, "%")
            try:
                value = float(other.value.split()[0])
            except ValueError:
                return super().coerce(other)
            return Unit(value)
        else:
            return super().coerce(other)
