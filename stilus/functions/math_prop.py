import math as m

from stilus.nodes.string import String
from stilus.nodes.unit import Unit


# todo: convert all javascript math functions to python and vice versa
def math_prop(prop: String, evaluator=None):
    """Get Math ``prop``"""
    if hasattr(m, prop.string):
        return Unit(getattr(m, prop.string))
    elif hasattr(m, str(prop.string.upper())):
        upper = prop.string.upper()
        return Unit(getattr(m, upper))
    elif hasattr(m, str(prop.string.lower())):
        lower = prop.string.lower()
        return Unit(getattr(m, lower))
    else:
        raise ValueError(f'Oops; could not return math.{prop}.')
