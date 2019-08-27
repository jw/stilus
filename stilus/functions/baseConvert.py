from stilus.nodes.expression import Expression
from stilus.nodes.literal import Literal
from stilus.utils import unwrap, assert_type


def _convert(num, base):
    convert_string = "0123456789abcdefghijklmnopqrstuvwxyz"
    if num < base:
        return convert_string[num]
    else:
        return _convert(num // base, base) + convert_string[num % base]


def base_convert(num, base, width=None, evaluator=None):
    if isinstance(num, Expression):
        num = unwrap(num).nodes[0]
    if isinstance(base, Expression):
        base = unwrap(base).nodes[0]
    if width and isinstance(width, Expression):
        width = unwrap(width).nodes[0]
    assert_type(num, 'unit')
    assert_type(base, 'unit')
    if width:
        assert_type(width, 'unit')
    if width:
        width = width.value
    else:
        width = 2
    num = int(num.value)
    base = int(base.value)
    result = _convert(num, base)
    while len(result) < width:
        result = '0' + result
    return Literal(result)
