from stilus.utils import unwrap


def unshift(expr, *args, evaluator=None):
    expr = unwrap(expr)
    for arg in args:
        a = unwrap(arg)
        expr.nodes.insert(0, a)
    return len(expr.nodes)
