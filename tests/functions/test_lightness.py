from functions.lightness import lightness
from nodes.color import HSLA
from nodes.unit import Unit


def test_lightness():
    color = HSLA(100, 50, 0, .5)
    assert lightness(color) == Unit(0, '%')
    color = HSLA(100, 50, 0, .5)
    assert lightness(color, Unit(70)) == HSLA(100, 50, 70, .5)
    assert lightness(color, Unit(400)) == HSLA(100, 50, 100, .5)
