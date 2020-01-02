from stilus.nodes.atblock import Atblock
from stilus.nodes.block import Block
from stilus.nodes.boolean import true
from stilus.nodes.node import Node
from stilus.nodes.null import null


def test_atblock():
    atblock = Atblock()
    assert atblock.node_name == "atblock"
    assert atblock.block is None
    assert atblock.nodes == []
    block = Block(Node(), Node())
    block.append(null)
    block.append(Node())
    block.append(true)
    atblock.block = block
    assert atblock.nodes == [null, Node(), true]
