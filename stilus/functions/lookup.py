from nodes.null import null
from utils import assert_type


def lookup(name, evaluator=None):
    assert_type(name, 'string', 'name')
    node = evaluator.lookup(name.value)
    if node:
        return evaluator.visit(node)
    else:
        return null
