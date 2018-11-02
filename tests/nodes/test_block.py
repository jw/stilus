from stilus.nodes.block import Block
from stilus.nodes.boolean import true
from stilus.nodes.comment import Comment
from stilus.nodes.expression import Expression
from stilus.nodes.literal import Literal
from stilus.nodes.media import Media
from stilus.nodes.null import null
from stilus.nodes.property import Property
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
    assert block.is_empty() is True


def test_block_push():
    block = Block(Comment("comment", False, False),
                  Block(String("hello"), String("There!")))
    block.push(Literal("Literal"))
    block.push(true)
    assert block.nodes == [Literal("Literal"), true]
    assert block.has_properties() is False
    assert block.has_media() is False
    assert block.is_empty() is False


def test_block_properties():
    block = Block(Comment("comment", False, False),
                  Block(String("hello"), String("There!")))
    block.push(Property(['foo', 'bar'], Expression()))
    assert block.has_properties() is True
    assert block.has_media() is False


def test_block_media():
    block = Block(Comment("comment", False, False),
                  Block(String("hello"), String("There!")))
    block.push(Media('fizz'))
    assert block.has_properties() is False
    assert block.has_media() is True