from stilus.functions.component import component
from stilus.nodes.color import RGBA, HSLA
from stilus.nodes.string import String
from stilus.nodes.unit import Unit


def test_component_hsla_hue():
    color = HSLA(200, 100, 50, 0.5)
    string = String("hue")
    unit = component(color, string)
    assert unit == Unit(200, "deg")


def test_component_hsla_saturation():
    color = HSLA(100, 100, 100, 0.5)
    string = String("saturation")
    unit = component(color, string)
    assert unit == Unit(100, "%")


def test_component_hsla_lightness():
    color = HSLA(100, 100, 50, 0.5)
    string = String("lightness")
    unit = component(color, string)
    assert unit == Unit(50, "%")


def test_component_rgba_hue():
    color = RGBA(200, 100, 50, 0.5)
    string = String("red")
    unit = component(color, string)
    assert unit == Unit(200, "deg")


def test_component_rgba_saturation():
    color = RGBA(100, 100, 100, 0.5)
    string = String("green")
    unit = component(color, string)
    assert unit == Unit(100, "%")


def test_component_rgba_lightness():
    color = RGBA(100, 100, 50, 0.5)
    string = String("blue")
    unit = component(color, string)
    assert unit == Unit(50, "%")
