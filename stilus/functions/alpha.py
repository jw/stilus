from typing import Type

from functions.rgba import rgba
from nodes.color import Color, HSLA
from nodes.unit import Unit


def alpha(color: Type[Color], value=None, evaluator=None):
    if isinstance(color, HSLA):
        color = color.rgba()
    if value:
        return rgba(Unit(color.r),
                    Unit(color.g),
                    Unit(color.b),
                    value,
                    evaluator)
    return Unit(color.a, '')
