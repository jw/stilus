from stilus.nodes.unit import Unit
from stilus.utils import assert_type, assert_string


def unit(unit, type, evaluator=None):
    assert_type(unit, 'unit', 'unit')

    if type:
        assert_string(type, 'type')
        return Unit(unit.value, type.string)
    else:
        return unit.type if unit.type else ''
