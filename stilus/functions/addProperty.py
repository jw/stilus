from stilus.nodes.property import Property
from stilus.utils import assert_type, unwrap, assert_string


def add_property(name, expr, evaluator=None):
    assert_type(name, 'expression', 'name')
    name = unwrap(name).first()
    assert_string(name, 'name')
    assert_type(expr, 'expression', 'expr')
    prop = Property([name], expr)
    block = evaluator.closest_block()
    head = block.nodes[0:block.index]
    tail = block.nodes[block.index:len(block.nodes)]
    block.index += 1
    head.append(prop)
    block.nodes = head.extend(tail)
    return prop
