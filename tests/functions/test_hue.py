from functions.hue import hue
from nodes.color import HSLA
from nodes.unit import Unit


def test_hue():
    color = HSLA(100, 50, 0, .5)
    assert hue(color) == Unit(100, 'deg')
    color = HSLA(100, 50, 0, .5)
    assert hue(color, Unit(200)) == HSLA(200, 50, 0, .5)
    assert hue(color, Unit(400)) == HSLA(40, 50, 0, .5)
