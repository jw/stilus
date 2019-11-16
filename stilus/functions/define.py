from nodes.ident import Ident
from nodes.null import null
from utils import assert_type, unwrap


def define(name, expr, common=None, evaluator=None):
    assert_type(name, 'string', 'name')
    expr = unwrap(expr)
    scope = evaluator.get_current_scope()
    if common and common.to_boolean().is_true():
        scope = evaluator.common.scope()
    node = Ident(name.value, expr)
    scope.add(node)
    return null
