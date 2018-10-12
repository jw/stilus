from stilus.nodes.expression import Expression
from stilus.nodes.node import Node


def unwrap(expression: Expression) -> Node:
    """
    Unwrap `expression`.
    Takes an expressions with length of 1
    such as `((1 2 3))` and unwraps it to `(1 2 3)`.

    :param expression:
    :return:
    """
    if expression.name not in ['arguments', 'expression']:
        return expression
    if expression.first().name not in ['arguments', 'expression']:
        return expression
    if len(expression) != 1:
        return expression
    if expression.preserve:
        return expression
    return unwrap(expression.first())


def assert_present(node: Node, name):
    if node:
        return
    if name:
        raise ValueError(f'"{name}" argument required')
    raise ValueError('argument missing')


def assert_color(node: Node, param):
    assert_present(node, param)
    if node.name not in ['rgba', 'hsla']:
        raise TypeError(f'TypeError: expected rgba or hsla, but got '
                        f'{node.name}:{node}')


def assert_string(node: Node, param):
    assert_present(node, param)
    if node.name in ['string', 'ident', 'literal']:
        return
    else:
        raise TypeError(f'TypeError: expected string, ident or literal, '
                        f'but got {node.name}:{node}')


def assert_type(node: Node, type, param):
    assert_present(node, param)
    if node.name == type:
        return
    p = f'{param} to be a ' if param else ''
    raise TypeError(f'expected {p}{type}, but got {node.name}:{node}')


def clamp(n, smallest=0, largest=255):
    return max(smallest, min(round(n), largest))


def clamp_alpha(n, smallest=0, largest=1):
    return max(smallest, min(n, largest))


def clamp_degrees(n):
    n = n % 360
    return n if n >= 0 else 360 + n


def clamp_percentage(n, smallest=0, largest=100):
    return max(smallest, min(n, largest))
