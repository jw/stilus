from stilus.utils import unwrap


def push(expr, *args, evaluator=None):
    expr = unwrap(expr)
    if evaluator:
        for arg in args:
            expr.nodes.append(unwrap(arg).clone())
    return len(expr.nodes)
