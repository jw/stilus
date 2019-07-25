from stilus.nodes.unit import Unit
from stilus.functions.hsla import hsla
from stilus.utils import assert_color


def hsl(hue, saturation, lightness):
    if hue and (saturation is lightness is None):
        assert_color(hue, 'color')
        return hue.hsla
    return hsla(hue, saturation, lightness, Unit(1))
