import math as m

from stilus.nodes.string import String
from stilus.nodes.unit import Unit
from stilus.utils import assert_type, assert_string, stilus_round


def math(n: Unit, fn: String, evaluator=None):
    """Apply Math ``fn`` to ``n``"""
    assert_type(n, "unit", "n")
    assert_string(fn, "fn")

    if fn.string == "round":
        return Unit(int(stilus_round(n.value)), n.type)

    return Unit(m.__getattribute__(fn.string)(n.value), n.type)
