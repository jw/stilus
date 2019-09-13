from stilus.utils import assert_present, assert_type


def operate(op=None, left=None, right=None, evaluator=None):
    assert_type(op, 'string', 'op')
    assert_present(left, 'left')
    assert_present(right, 'right')
    return left.operate(op.value, right)
