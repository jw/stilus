import logging

import math as m
from stilus.nodes.unit import Unit
from stilus.utils import assert_type, stilus_round

log = logging.getLogger(__name__)


def tan(angle, evaluator=None):
    assert_type(angle, 'unit', 'angle')
    radians = angle.value
    if angle.type == 'deg':
        radians = m.radians(radians)
    pow = m.pow(10, 9)
    sin = float(stilus_round(m.sin(radians) * pow)) / pow
    cos = float(stilus_round(m.cos(radians) * pow)) / pow
    if cos == 0:
        tan = 'Infinity'
    else:
        tan = float(stilus_round(pow * sin / cos)) / pow
    if tan == 0:
        tan = 0
    # return Unit(m.tan(radians), '')
    return Unit(tan, '')
