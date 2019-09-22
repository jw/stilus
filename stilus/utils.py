import types
from decimal import Decimal, ROUND_HALF_UP
from os.path import join
from pathlib import Path
from typing import List

from stilus.nodes.boolean import Boolean
from stilus.nodes.expression import Expression
from stilus.nodes.literal import Literal
from stilus.nodes.node import Node
from stilus.nodes.null import null, Null
from stilus.nodes.object_node import ObjectNode
from stilus.nodes.string import String
from stilus.nodes.unit import Unit
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
    if node or isinstance(node, Null):
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


def assert_type(node: Node, type, param=None):
    assert_present(node, param)
    if node.node_name == type:
        return
    p = f'{param} to be a ' if param else ''
    raise TypeError(f'expected {p}{type}, but got {node.node_name}:{node}')


def clamp(n, smallest=0, largest=255):
    return max(smallest, min(int(stilus_round(n)), largest))


def stilus_round(n):
    return Decimal(n).quantize(Decimal(1), rounding=ROUND_HALF_UP)


def clamp_alpha(n, smallest=0, largest=1):
    return max(smallest, min(n, largest))


def clamp_degrees(n):
    n = n % 360
    return n if n >= 0 else 360 + n


def clamp_percentage(n, smallest=0, largest=100):
    return max(smallest, min(n, largest))


def compile_selectors(arr, leave_hidden=False, indent=''):
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
    indent = indent
    buf = []

    def parse(selector, buf):
        parts = [selector.value]
        parents = []
        string = SelectorParser(parts[0], parents, parts).parse()['value']

        if buf:
            for i, part in enumerate(buf):
                parts.append(part)
                parents.append(string)
                child = SelectorParser(buf[i], parents, parts).parse()

                # todo: fix this
                if child['nested']:
                    string += ' ' + child['value']
                else:
                    string = child['value']

        return string.strip()

    def compile(arr, i):
        if i:
            for selector in arr[i]:
                if not leave_hidden and selector.is_placeholder():
                    return
                if selector.inherits:
                    buf.insert(0, selector.value)
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

    # return unique selectors
    return list(dict.fromkeys(selectors))


# todo: check deep parameter; check why this method exists
def merge(a, b):
    """Merges two dicts.  How weird."""
    return a.update(b)


# todo: use libpath
def lookup(path: Path, paths: List, ignore=''):
    if isinstance(path, Path):
        p = path
    else:
        p = Path(path)
    if p.is_absolute() and p.exists():
        return str(path)

    for a_path in paths:
        lookup = join(a_path, path)
        if ignore == lookup:
            continue
        p = Path(lookup).resolve()
        if p.exists():
            return str(lookup)

    return None


def find(path, paths, ignore):
    # first see if path exists
    p = Path(path)
    if p.is_absolute() and p.exists():
        return [str(p)]

    # if not see if it is in paths
    for base in reversed(paths):
        lookup = Path(join(base, path))
        if lookup == ignore:
            continue
        if '*' in path:
            found = sorted(Path(base).glob(path))
            if found:
                return [str(file) for file in found]
        else:
            if lookup.exists():
                return [str(lookup.resolve())]

    return None


def lookup_index(name, paths, filename):

    found = find(join(name, 'index.styl'), paths, filename)
    # todo: check basename replacement?
    # todo: check node modules?
    return found


def coerce_list(value, raw, lineno=1, column=1):
    expr = Expression(lineno=lineno, column=column)
    for v in value:
        expr.append(coerce(v, raw, lineno=lineno, column=column))
    return expr


def coerce_object(object, raw, lineno=1, column=1):
    # todo: this needs tests!
    node = ObjectNode() if raw else Expression()
    for key in object:
        value = coerce(object[key], raw, lineno=lineno, column=column)
        if raw:
            node[key] = value
        else:
            node.append(coerce_list([key, value], False))
    return node


def coerce(value, raw: bool, lineno=1, column=1):
    if isinstance(value, types.FunctionType):
        return value
    elif isinstance(value, str):
        return String(value, lineno=lineno, column=column)
    elif isinstance(value, bool):
        return Boolean(value, lineno=lineno, column=column)
    elif isinstance(value, int):
        return Unit(value, lineno=lineno, column=column)
    elif isinstance(value, list):
        return coerce_list(value, raw, lineno=lineno, column=column)
    elif value is None:
        return null
    elif hasattr(value, 'node_name'):
        return value
    else:
        coerce_object(value, raw, lineno=lineno, column=column)


def parse_string(str: String):
    from stilus.parser import Parser
    try:
        parser = Parser(str, {})
        result = parser.list()
    except BaseException:
        result = Literal(str)
    return result
