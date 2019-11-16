from nodes.null import null
from utils import unwrap


def pop(expr, *args, evaluator=None):
    expr = unwrap(expr)
    if len(expr.nodes) > 0:
        return expr.nodes.pop()
    else:
        return null
