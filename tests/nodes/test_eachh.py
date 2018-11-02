from stilus.nodes.block import Block
from stilus.nodes.eachh import Eachh
from stilus.nodes.expression import Expression
from stilus.nodes.node import Node


def test_property():
    expression = Expression()
    block = Block('parent', Node)
    eachh = Eachh('foo', 'fizz', expression, block)
    assert eachh.name == 'eachh'
    assert eachh.value == 'foo'
    assert eachh.key == 'fizz'
    assert eachh.expression == expression
    assert eachh.block == block
