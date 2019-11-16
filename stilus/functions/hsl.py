from nodes.unit import Unit
from functions.hsla import hsla
from utils import assert_color


def hsl(hue, saturation=None, lightness=None, evaluator=None):
    if hue and (saturation is lightness is None):
        assert_color(hue, 'color')
        return hue.hsla()
    return hsla(hue, saturation, lightness, Unit(1), evaluator)
