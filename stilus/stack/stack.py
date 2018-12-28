from typing import Type

from deprecated import deprecated

from stilus.nodes.block import Block
from stilus.nodes.node import Node
from stilus.stack.frame import Frame


class Stack(list):

    def __init__(self):
        """Create a stack"""
        super().__init__()

    def __str__(self):
        buffer = []
        for frame in self:
            node = frame.block.node
            location = f'({node.filename}:{node.lineno}:{node.column})'
            if node.name == 'function':
                buffer.append(f'    at {node.node_name}() {location}')
            elif node.name == 'group':
                buffer.append(f'    at "{node.nodes[0].value}" {location}')
        return '\n'.join(buffer)

    def __repr__(self):
        return self.__str__()

    @deprecated(reason='use append')
    def push(self, frame: Frame):
        return self.append(frame)

    def append(self, frame: Frame):
        """Push a frame to the stack."""
        frame.stack = self
        frame.parent = self.current_frame()
        return super().append(frame)

    def current_frame(self: Frame):
        """Get the current frame."""
        if len(self) == 0:
            return None
        else:
            return self[self.__len__() - 1]

    def get_block_frame(self, block: Block):
        """Lookup stack frame for a given block"""
        for i in range(self.__len__()):
            if block == self[i].block:
                return self[i]
        return None

    def lookup(self, name) -> Type[Node]:
        """Lookup the given local variable `name`, relative to the lexical
        scope of the current frame's `Block`.
        When the result of a lookup is an identifier a recursive lookup
        is performed, defaulting to returning the identifier itself.
        :param name: local variable
        :return:
        """
        block = None
        if self.current_frame():
            block = self.current_frame().block
        while True:
            frame = self.get_block_frame(block)
            if frame:
                val = frame.lookup(name)
                if val:
                    return val
            if hasattr(block, 'parent'):
                block = block.parent
            else:
                block = None
            if block is None:
                return
