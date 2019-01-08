from stilus.nodes.expression import Expression
from stilus.nodes.node import Node
from stilus.selector_parser import SelectorParser


def unwrap(expression: Expression) -> Node:
    """
    Unwrap `expression`.
    Takes an expressions with length of 1
    such as `((1 2 3))` and unwraps it to `(1 2 3)`.

    :param expression:
    :return:
    """
    if hasattr(expression, 'preserve') and expression.preserve:
        return expression
    if expression.node_name not in ['arguments', 'expression']:
        return expression
    if len(expression) != 1:
        return expression
    if expression.nodes[0].node_name not in ['arguments', 'expression']:
        return expression
    return unwrap(expression.nodes[0])


def assert_present(node: Node, name=None):
    if node:
        return
    if name:
        raise ValueError(f'"{name}" argument required')
    raise ValueError('argument missing')


def assert_color(node: Node, param=Node):
    assert_present(node, param)
    if node.node_name not in ['rgba', 'hsla']:
        raise TypeError(f'TypeError: expected rgba or hsla, but got '
                        f'{node.node_name}:{node}')


def assert_string(node: Node, param):
    assert_present(node, param)
    if node.node_name in ['string', 'ident', 'literal']:
        return
    else:
        raise TypeError(f'TypeError: expected string, ident or literal, '
                        f'but got {node.node_name}:{node}')


def assert_type(node: Node, type, param):
    assert_present(node, param)
    if node.node_name == type:
        return
    p = f'{param} to be a ' if param else ''
    raise TypeError(f'expected {p}{type}, but got {node.node_name}:{node}')


def clamp(n, smallest=0, largest=255):
    return max(smallest, min(round(n), largest))


def clamp_alpha(n, smallest=0, largest=1):
    return max(smallest, min(n, largest))


def clamp_degrees(n):
    n = n % 360
    return n if n >= 0 else 360 + n


def clamp_percentage(n, smallest=0, largest=100):
    return max(smallest, min(n, largest))


def compile_selectors(arr, leave_hidden=False):
    """
    Compile selector strings in `arr` from the bottom-up
    to produce the selector combinations. For example
    the following Stylus:

    '''
    ul
      li
      p
        a
          color: red
    '''

    would return:

      [ 'ul li a', 'ul p a' ]

    :param arr:
    :param leave_hidden:
    :return:
    """
    selectors = []
    indent = ''  # todo: compiler.indent; move it to utils?
    buf = []

    def parse(selector, buf):
        parts = [selector.value]
        parents = []
        string = SelectorParser(parts[0], parents, parts).parse()['val']

        if buf:
            for i, part in enumerate(buf):
                parts.append(part)
                parents.append(string)
                child = SelectorParser(buf[i], parents, parts).parse()

                if child.nested:
                    string += ' ' + child.value
                else:
                    string = child.val

        return string.strip()

    def compile(arr, i):
        if i:
            for selector in arr[i]:
                if not leave_hidden and selector.is_placeholder():
                    return
                if selector.inherits:
                    buf.insert(0, selector.val)
                    compile(arr, i - 1)
                    buf.pop(0)
                else:
                    selectors.append(indent + parse(selector, buf))
        else:
            for selector in arr[0]:
                if not leave_hidden and selector.is_placeholder():
                    return
                string = parse(selector, buf)
                if string:
                    selectors.append(indent + string)

    compile(arr, len(arr) - 1)

    return set(selectors)


def merge(a, b, deep: bool):
    """Merges two dicts.  How weird."""
    return a.update(b)
