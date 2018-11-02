from stilus.nodes.unaryop import UnaryOp
from stilus.nodes.expression import Expression


def test_binop():
    expression = Expression()
    unaryop = UnaryOp('+', expression)
    assert unaryop.name == 'unaryop'
    assert unaryop.op == '+'
    assert unaryop.expr == expression
    assert f'{unaryop}' == f'(+,{expression})'
