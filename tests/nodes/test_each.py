from stilus.nodes.block import Block
from stilus.nodes.each import Each
from stilus.nodes.expression import Expression
from stilus.nodes.node import Node


def test_property():
    expression = Expression()
    block = Block('parent', Node)
    each = Each('foo', 'fizz', expression, block)
    assert each.node_name == 'each'
    assert each.value == 'foo'
    assert each.key == 'fizz'
    assert each.expr == expression
    assert each.block == block
