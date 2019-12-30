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
    assert block.node_name == "block"
    assert block.is_empty() is True


def test_block_append():
    block = Block(
        Comment("comment", False, False),
        Block(String("hello"), String("There!")),
    )
    block.append(Literal("Literal"))
    block.append(true)
    assert block.nodes == [Literal("Literal"), true]
    assert block.has_properties() is False
    assert block.has_media() is False
    assert block.is_empty() is False


def test_block_properties():
    block = Block(
        Comment("comment", False, False),
        Block(String("hello"), String("There!")),
    )
    block.append(Property(["foo", "bar"], Expression()))
    assert block.has_properties() is True
    assert block.has_media() is False


def test_block_media():
    block = Block(
        Comment("comment", False, False),
        Block(String("hello"), String("There!")),
    )
    block.append(Media("fizz"))
    assert block.has_properties() is False
    assert block.has_media() is True
