import logging

from stilus.functions import math
from stilus.nodes.unit import Unit
from stilus.utils import assert_type

log = logging.getLogger(__name__)


def tan(angle, evaluator=None):
    assert_type(angle, 'unit', 'angle')
    radians = angle.value
    if angle.type == 'deg':
        radians *= math.pi / 180
    return Unit(math.tan(radians), '')
