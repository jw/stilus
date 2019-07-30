from stilus.functions.rgba import rgba
from stilus.nodes.color import Color, HSLA
from stilus.nodes.unit import Unit


def blue(color: Color, value: Unit = None, evaluator=None):
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
    if isinstance(color, HSLA):
        color = color.rgba()
    if value:
        return rgba(Unit(color.r),
                    Unit(color.g),
                    value,
                    Unit(color.a),
                    evaluator)
    return Unit(color.b, '')
