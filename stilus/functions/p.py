from stilus.nodes.null import null
from stilus.utils import unwrap


def p(*args, evaluator=None):
    for arg in args:
        expr = unwrap(arg)
        if not expr:
            return None
        e = str(expr)
        if e.startswith("("):
            e = e[1:]
        if e.endswith(")"):
            e = e[:-1]
        print(f"inspect: {e}")
    return null
