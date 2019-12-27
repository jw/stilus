from stilus.exceptions import StilusError
from stilus.nodes.expression import Expression
from stilus.nodes.unit import Unit
from stilus.utils import assert_type


def range_function(start, stop, step=None, evaluator=None):
    assert_type(start, 'unit', 'start')
    assert_type(stop, 'unit', 'stop')
    if step:
        assert_type(step, 'unit', 'step')
        if step.value == 0:
            raise StilusError('ArgumentError: "step" argument '
                              'must not be zero')
    else:
        step = Unit(1)
    lst = Expression()
    i = start.value
    while i <= stop.value:
        lst.append(Unit(i, start.type))
        i += step.value
    return lst
