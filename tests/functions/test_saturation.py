from functions.saturation import saturation
from nodes.color import HSLA
from nodes.unit import Unit


def test_saturation():
    color = HSLA(100, 50, 0, .5)
    assert saturation(color) == Unit(50, '%')
    color = HSLA(100, 50, 0, .5)
    assert saturation(color, Unit(70)) == HSLA(100, 70, 0, .5)
    assert saturation(color, Unit(400)) == HSLA(100, 100, 0, .5)
