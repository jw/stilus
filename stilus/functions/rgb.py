from functions.rgba import rgba
from nodes.color import RGBA
from nodes.unit import Unit
from utils import assert_color


def rgb(red, green, blue, evaluator=None):
    if red and (green is blue is None):
        assert_color(red)
        color = red.rgba()
        return RGBA(color.r, color.g, color.b, 1)
    return rgba(red, green, blue, Unit(1), evaluator)
