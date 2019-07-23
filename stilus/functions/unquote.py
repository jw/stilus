from stilus.nodes.literal import Literal
from stilus.utils import assert_string


def unquote(string):
    assert_string(string, 'string')
    return Literal(string.string)
