from typing import Type

from stilus.functions.rgba import rgba
from stilus.nodes.color import Color, HSLA
from stilus.nodes.unit import Unit


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
