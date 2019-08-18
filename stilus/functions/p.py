from stilus.nodes.null import null
from stilus.utils import unwrap


def p(*args, evaluator=None):
    for arg in args:
        expr = unwrap(arg)
        if not expr:
            return None
        e = str(expr).replace('(',  '').replace(')', '')
        print(f'inspect: {e}')
    return null
