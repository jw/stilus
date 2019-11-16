from nodes.unaryop import UnaryOp
from nodes.expression import Expression


def test_binop():
    expression = Expression()
    unaryop = UnaryOp('+', expression)
    assert unaryop.node_name == 'unaryop'
    assert unaryop.op == '+'
    assert unaryop.expr == expression
    assert f'{unaryop}' == f'(+,{expression})'
