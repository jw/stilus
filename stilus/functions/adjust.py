from stilus.functions import saturation
from stilus.functions.hue import hue
from stilus.utils import assert_color, assert_string, assert_type


def adjust(color, prop, amount):
    assert_color(color, 'color')
    assert_string(prop, 'prop')
    assert_type(amount, 'unit', 'amount')
    hsl = color.hsla.clone()
    prop = {hue: 'h',
            saturation: 's',
            lightness: 'l'}[prop.string]
    if not prop:
        raise TypeError('invalid adjustment property')
    val = amount.val
    if amount.type == '%':
        if 'l' == prop and val > 0:
            val = (100 - hsl[prop]) * val / 100
        else:
            val = hsl[prop] * (val / 100)
    hsl[prop] += val
    return hsl.rgba
