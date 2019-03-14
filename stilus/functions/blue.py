from stilus.functions.rgba import rgba
from stilus.nodes.color import Color
from stilus.nodes.unit import Unit


def blue(color: Color, value: Unit = None):
    """Return the blue component of the given `color`, or set the blue
    component to the optional second `value` argument.

    >>> blue(#00c)
    204

    >>> blue(#000, 255)
    #00f

    :param color:
    :param value:
    :return:
    """
    c = color.rgba
    if value:
        return rgba(Unit(c.r), Unit(c.g), value, Unit(c.a))
    return Unit(c.b, '')
