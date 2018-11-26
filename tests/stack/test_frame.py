from stilus.nodes.block import Block
from stilus.nodes.ident import Ident
from stilus.stack.frame import Frame
from stilus.stack.scope import Scope


def test_frame():
    frame = Frame(Block(Ident('hello'), Ident('there')))
    assert frame.scope() == Scope()
    assert frame.block == Block(Ident('hello'), Ident('there'))
    assert frame.parent is None
    block = Block(Ident('hello'), Ident('there'))
    block.scope = False
    parent_block = Block(Ident('parent'), Ident('node'))
    frame = Frame(block, parent_block)
    assert frame.scope() == Scope()
    assert frame.block == block
    assert frame.parent == parent_block


def test_frame_lookup():
    frame = Frame(Block('hello', 'there'))
    scope = Scope()
    scope.add(Ident('foo', 'bar'))
    frame._scope = scope
    assert frame.lookup('foo') == 'bar'
    assert frame.lookup('unknown') is None
