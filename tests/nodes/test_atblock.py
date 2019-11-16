from nodes.atblock import Atblock
from nodes.block import Block
from nodes.boolean import true
from nodes.node import Node
from nodes.null import null


def test_atblock():
    atblock = Atblock()
    assert atblock.node_name == 'atblock'
    assert atblock.block is None
    assert atblock.nodes == []
    block = Block(Node(), Node())
    block.append(null)
    block.append(Node())
    block.append(true)
    atblock.block = block
    assert atblock.nodes == [null, Node(), true]
