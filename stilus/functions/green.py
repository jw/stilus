from typing import Type

from functions.rgba import rgba
from nodes.color import Color, HSLA
from nodes.unit import Unit


def green(color: Type[Color], value=None, evaluator=None):
    if isinstance(color, HSLA):
        color = color.rgba()
    if value:
        return rgba(Unit(color.r),
                    value,
                    Unit(color.b),
                    Unit(color.a),
                    evaluator)
    return Unit(color.g, '')
