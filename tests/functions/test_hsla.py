from functions.hsla import hsla
from nodes.color import HSLA
from nodes.unit import Unit


def test_hsla_color():
    color = HSLA(0, 50, 0, .5)
    assert hsla(color) == HSLA(0, 50, 0, .5)


def test_hsla_alpha():
    color = HSLA(0, 100, 0, .5)
    alpha = Unit(66, '%')
    assert hsla(color, alpha) == HSLA(0, 100, 0, .66)
    color = HSLA(0, 100, 0, .5)
    alpha = Unit(.3)
    assert hsla(color, alpha) == HSLA(0, 100, 0, .3)


def test_hsla_components():
    hue = Unit(20)
    saturation = Unit(40)
    lightness = Unit(60)
    alpha = Unit(.8)
    assert hsla(hue, saturation, lightness, alpha) == HSLA(20, 40, 60, .8)
    alpha = Unit(90, '%')
    assert hsla(hue, saturation, lightness, alpha) == HSLA(20, 40, 60, .9)
    hue = Unit(20, 'deg')
    saturation = Unit(40, '%')
    lightness = Unit(60, '%')
    alpha = Unit(80, '%')
    assert hsla(hue, saturation, lightness, alpha) == HSLA(20, 40, 60, .8)


def test_hsla_components_weird():
    hue = Unit(20, 'mm')
    saturation = Unit(40, 'mm')
    lightness = Unit(60, 'in')
    alpha = Unit(.8, 'kHz')
    assert hsla(hue, saturation, lightness, alpha) == HSLA(20, 40, 60, .8)


def test_hsla_components_clamping():
    hue = Unit(120)
    saturation = Unit(140)
    lightness = Unit(160)
    alpha = Unit(190, '%')
    assert hsla(hue, saturation, lightness, alpha) == HSLA(120, 100, 100, 1.)
    hue = Unit(380)
    saturation = Unit(140)
    lightness = Unit(160)
    alpha = Unit(190, '%')
    assert hsla(hue, saturation, lightness, alpha) == HSLA(20, 100, 100, 1.)
