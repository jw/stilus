from stilus.nodes.block import Block
from stilus.nodes.boolean import true
from stilus.nodes.comment import Comment
from stilus.nodes.literal import Literal
from stilus.nodes.null import null
from stilus.nodes.string import String


def test_block():
    block = Block(null, true)
    assert block.nodes == []
    assert block.scope is True
    assert block.node == true
    assert block.parent == null
    assert block.name == 'block'
    clone = block.clone()
    assert clone == block


def test_block_push():
    block = Block(Comment("comment", False, False),
                  Block(String("hello"), String("There!")))
    block.push(Literal("Literal"))
    block.push(true)
    assert block.nodes == [Literal("Literal"), true]
