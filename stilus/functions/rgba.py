from stilus.nodes.color import RGBA
from stilus.utils import assert_color, assert_type


def rgba(red, green=None, blue=None, alpha=None, evaluator=None):
    """Return a `RGBA` from the r,g,b,a channels.

    >>> rgba(255,0,0,0.5)
    rgba(255,0,0,0.5)
    >>> rgba(255,0,0,1)
    #ff0000
    >>> rgba(#ffcc00, 50%)
    rgba(255,204,0,0.5)

    :param red:
    :param green:
    :param blue:
    :param alpha:
    :return:
    """
    # color
    if red and (green is blue is alpha is None):
        assert_color(red)
        return red.rgba()
    # alpha
    if red and green and (blue is alpha is None):
        assert_color(red)
        color = red.rgba()
        assert_type(green, 'unit', 'alpha')
        alpha = green.clone()
        if alpha.type == '%':
            alpha.value /= 100
        return RGBA(color.r, color.g, color.b, alpha.value)
    # color
    assert_type(red, 'unit', 'red')
    assert_type(green, 'unit', 'green')
    assert_type(blue, 'unit', 'blue')
    assert_type(alpha, 'unit', 'alpha')
    r = round(red.value * 2.55) if red.type == '%' else red.value
    g = round(green.value * 2.55) if green.type == '%' else green.value
    b = round(blue.value * 2.55) if blue.type == '%' else blue.value

    alpha = alpha.clone()
    if alpha and alpha.type == '%':
        alpha.value /= 100

    return RGBA(r, g, b, alpha.value)
