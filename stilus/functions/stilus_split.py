from stilus.nodes.expression import Expression
from stilus.nodes.ident import Ident
from stilus.nodes.string import String
from stilus.utils import assert_string


def split(delim, value, evaluator=None):
    assert_string(delim, 'delimiter')
    assert_string(value, 'val')
    words = value.string.split(delim.string)
    expr = Expression()
    for word in words:
        if isinstance(value, Ident):
            addition = Ident(word)
        else:
            addition = String(word)
        expr.append(Ident(addition))
    return expr
