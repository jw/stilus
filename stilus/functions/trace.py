import math

from stilus.nodes.unit import Unit
from stilus.utils import assert_type


def trace(angle, evaluator=None):
    assert_type(angle, 'unit', 'angle')
    radians = angle.value
    if angle.type == 'deg':
        radians *= math.pi / 180
    return Unit(math.tan(radians), '')
