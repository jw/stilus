from nodes.ident import Ident
from nodes.string import String
from utils import assert_string, assert_type


def substr(value, start, length=None, evaluator=None):
    assert_string(value, 'val')
    assert_type(start, 'unit', 'start')
    start = int(start.value)
    if length:
        length = start + int(length.value)
    result = value.string[start:length]
    if isinstance(value, Ident):
        return Ident(result)
    else:
        return String(result)
