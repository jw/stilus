from stilus.nodes.block import Block
from stilus.nodes.ident import Ident
from stilus.stack.frame import Frame
from stilus.stack.stack import Stack


def test_stack():
    stack = Stack()
    block = Block(Ident('hello', 'there'), Ident('foo', 'bar'))
    frame = Frame(block)
    stack.push(frame)
    assert len(stack) == 1
    assert stack.get_block_frame(block) == frame
    assert stack.current_frame() == frame
