from stilus.utils import assert_present


def clone(expr, evaluator=None):
    assert_present(expr, 'expr')
    return expr.clone()
