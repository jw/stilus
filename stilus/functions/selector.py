from stilus import utils
from stilus.selector_parser import SelectorParser
from stilus.utils import assert_string, compile_selectors


def parse(selector):
    from stilus.parser import Parser
    parser = Parser(selector, {})
    parser.state.append('selector-parts')
    nodes = parser.stmt_selector()
    for node in nodes:
        node.value = ''.join([str(segment) for segment in node.segments])
    return nodes


def push_to_stack(selectors, stack):
    for selector in selectors:
        selector = selector.first()
        assert_string(selector, 'selector')
        stack.append(parse(selector.string))


def selector(*args, evaluator=None):
    stack = evaluator.selector_stack()

    if len(args) == 1:
        expr = utils.unwrap(args[0])
        length = len(expr.nodes)

        # selector .a
        if length == 1:
            assert_string(expr.first(), 'selector')
            value = expr.first().string
            parsed = SelectorParser(value).parse()['value']

            if parsed == value:
                return value

            stack.append(parse(value))

        elif length > 1:
            # selector-list = '.a', '.b', '.c'
            # selector(selector-list)
            if expr.is_list:
                push_to_stack(expr.nodes, stack)
            # selector('.a' '.b' '.c')
            else:
                joined = ' '.join([node.string for node in expr.nodes])
                stack.append(parse(joined))

    # selector('.a', '.b', '.c')
    elif len(args) > 1:
        push_to_stack(args, stack)

    if stack:
        return ','.join(compile_selectors(stack))
    else:
        return '&'
