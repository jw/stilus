from stilus.nodes.binop import BinOp
from stilus.nodes.expression import Expression


def test_binop():
    left = Expression()
    right = Expression()
    binop = BinOp('+', left, right)
    assert binop.node_name == 'binop'
    assert binop.op == '+'
    assert binop.left == left
    assert binop.left == right
    assert f'{binop}' == f'{left} + {right}'
