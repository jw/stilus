from nodes.block import Block
from nodes.ident import Ident
from stack.frame import Frame
from stack.stack import Stack


def test_stack():
    stack = Stack()
    block = Block(Ident('hello', 'there'), Ident('foo', 'bar'))
    assert stack.get_block_frame(block) is None
    frame = Frame(block)
    stack.append(frame)
    assert len(stack) == 1
    assert stack.get_block_frame(block) == frame
    assert stack.current_frame() == frame


def test_empty_stack():
    stack = Stack()
    assert len(stack) == 0
    assert stack.current_frame() is None
    block = Block(Ident('hello', 'there'), Ident('foo', 'bar'))
    assert stack.get_block_frame(block) is None
