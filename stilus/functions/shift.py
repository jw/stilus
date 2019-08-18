from stilus.nodes.null import null
from stilus.utils import unwrap


def shift(expr, *args, evaluator=None):
    expr = unwrap(expr)
    if len(expr.nodes) > 0:
        return expr.nodes.pop(0)
    else:
        return null
