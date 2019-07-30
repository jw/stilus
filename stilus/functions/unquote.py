from stilus.nodes.literal import Literal
from stilus.utils import assert_string


def unquote(string, evaluator=None):
    assert_string(string, 'string')
    return Literal(string.string)
