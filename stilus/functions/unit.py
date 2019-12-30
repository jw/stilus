from stilus.nodes.unit import Unit
from stilus.utils import assert_string


def unit(unit, type=None, evaluator=None):
    # assert_type(unit, 'unit', 'unit')

    if type:
        assert_string(type, "type")
        return Unit(unit.value, type.string)
    else:
        return unit.type if hasattr(unit, "type") and unit.type else ""
