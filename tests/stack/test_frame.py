from pytest import raises

from stilus.nodes.block import Block
from stilus.nodes.ident import Ident
from stilus.stack.frame import Frame
from stilus.stack.scope import Scope


def test_frame_creation():
    frame = Frame(Block(Ident('hello'), Ident('there')))
    assert frame.scope() == Scope()
    assert frame.block == Block(Ident('hello'), Ident('there'))
    assert frame.parent is None


def test_frame_scopes():
    # regular block (scope is True) and frame has no parent -> scope == Scope()
    block = Block(Ident('hello'), Ident('there'))
    frame = Frame(block)
    assert frame.scope() == Scope()
    assert frame.block == block
    assert frame.parent is None
    # irregular block (scope is False) frame has no parent...
    block = Block(Ident('hello'), Ident('there'), scope=False)
    frame = Frame(block)
    # ...raises TypeError since no parent
    with raises(TypeError):
        frame.scope()
    assert frame.block == block
    assert frame.parent is None
    # regular block (scope is True) and frame has a parent -> scope == Scope()
    block = Block(Ident('hello'), Ident('there'))
    parent = Block(Ident('fizz'), Ident('fuzz'))
    frame = Frame(block, parent)
    assert frame.scope() == Scope()
    assert frame.block == block
    assert frame.parent is parent


def test_frame_str():
    block = Block('hello', 'there')
    frame = Frame(block)
    assert str(frame) == '[Frame [Scope]]'
    block.scope = False
    frame = Frame(block)
    assert str(frame) == '[Frame scope-less]'


def test_frame_lookup():
    frame = Frame(Block('hello', 'there'))
    scope = Scope()
    scope.add(Ident('foo', 'bar'))
    frame._scope = scope
    assert frame.lookup('foo') == 'bar'
    assert frame.lookup('unknown') is None
