from stilus.nodes.property import Property
from stilus.utils import assert_type, unwrap
# from stilus.visitor.evaluator import Evaluator


# this is a very weird function; it uses evaluator and
# does in fact almost the same as the evaluator.mixin()
# function?
# todo: fix me, implement me
def addProperty(name, expr):
    assert_type(name, 'expression', 'name')
    name = unwrap(name).first()
    assert_type(name, 'name')
    assert_type(expr, 'expression', 'expr')
    prop = Property([name], expr)
    block = None  # Evaluator.closest_block()  # from evaluator?
    head = block.nodes[0:block.index]
    tail = block.nodes[block.index:len(block.nodes)]
    block.index += 1
    head.push(prop)
    block.nodes = head.extend(tail)
    return prop
