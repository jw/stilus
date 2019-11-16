from nodes.string import String
from nodes.ident import Ident
from utils import assert_string


def replace(pattern, replacement, value, evaluator=None):
    assert_string(pattern, 'pattern')
    assert_string(replacement, 'replacement')
    assert_string(value, 'value')
    result = value.string.replace(pattern.string, replacement.string)
    if isinstance(value, Ident):
        return Ident(result)
    else:
        return String(result)
