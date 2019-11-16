from nodes.literal import Literal
from utils import assert_string


def unquote(string, evaluator=None):
    assert_string(string, 'string')
    return Literal(string.string)
