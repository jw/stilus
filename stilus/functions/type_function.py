from stilus.utils import assert_present


def type_function(node, evaluator=None):
    assert_present(node, 'expression')
    return node.node_name
