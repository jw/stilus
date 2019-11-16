from nodes.ternary import Ternary
from nodes.expression import Expression


def test_ternary():
    true_expression = Expression()
    false_expression = Expression()
    ternary = Ternary('+', true_expression, false_expression)
    assert ternary.node_name == 'ternary'
    assert ternary.cond == '+'
    assert ternary.true_expr == true_expression
    assert ternary.false_expr == false_expression
    assert f'{ternary}' == f'(+,{true_expression},{false_expression})'
