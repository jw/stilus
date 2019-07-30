from stilus.nodes.color import HSLA
from stilus.utils import assert_color, assert_type


def hsla(hue, saturation=None, lightness=None, alpha=None, evaluator=None):
    """Convert the given `color` to an `HSLA` node, or h,s,l,a component
    values.
    :param hue:
    :param saturation:
    :param lightness:
    :param alpha:
    :return: :class:HSLA
    """
    # color
    if hue and (saturation is lightness is alpha is None):
        assert_color(hue)
        return hue.hsla()
    # alpha
    if hue and saturation and (lightness is alpha is None):
        assert_color(hue)
        color = hue.hsla()
        assert_type(saturation, 'unit', 'alpha')
        alpha = saturation.clone()
        if alpha.type == '%':
            alpha.value /= 100
        return HSLA(color.hue, color.saturation, color.lightness, alpha.value)
    # color
    assert_type(hue, 'unit', 'hue')
    assert_type(saturation, 'unit', 'saturation')
    assert_type(lightness, 'unit', 'lightness')
    assert_type(alpha, 'unit', 'alpha')
    alpha = alpha.clone()
    if alpha and alpha.type == '%':
        alpha.value /= 100
    return HSLA(hue.value,
                saturation.value,
                lightness.value,
                alpha.value)
