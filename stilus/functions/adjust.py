from stilus.exceptions import StilusError
from stilus.utils import assert_color, assert_string, assert_type


def adjust(color, prop, amount, evaluator=None):
    assert_color(color, 'color')
    assert_string(prop, 'prop')
    assert_type(amount, 'unit', 'amount')
    hsl = color.hsla().clone()
    if not hasattr(hsl, prop.string):
        raise StilusError('Invalid adjustment property.')
    value = amount.value
    if amount.type == '%':
        if prop.string == 'lightness' and value > 0:
            value = (100 - hsl.lightness) * value / 100
        else:
            value = getattr(hsl, prop.string) * (value / 100)
    setattr(hsl, prop.string, getattr(hsl, prop.string) + value)
    return hsl.rgba()
