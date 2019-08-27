from typing import Type

from stilus.nodes.block import Block
from stilus.nodes.node import Node
from stilus.stack.frame import Frame


class Stack(list):
    """A stack of Frames."""

    def __init__(self):
        """Create an empty ``Frame`` stack"""
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

    def __next__(self):
        return super(next())

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
            return self[-1]

    def get_block_frame(self, block: Block):
        """Lookup stack frame for a given block"""
        for frame in self:
            # print(f'Checking equality between {block} and {frame.block}...')
            if block == frame.block:
                # print('equal!')
                return frame
        return None

    def lookup(self, name) -> Type[Node]:
        """Lookup the given local variable `name`, relative to the lexical
        scope of the current frame's `Block`.
        When the result of a lookup is an identifier a recursive lookup
        is performed, defaulting to returning the identifier itself.
        :param name: local variable
        :return:
        """
        # print(f'lookup: {name}...')
        block = None
        if self.current_frame():
            block = self.current_frame().block
        while True:
            frame = self.get_block_frame(block)
            if frame:
                val = frame.lookup(name)
                if val is not None:  # fixme: use val: (fix __len__)
                    # print(f'returning {val}!')
                    return val
            if hasattr(block, 'parent'):
                block = block.parent
            else:
                block = None
            if block is None:
                # print(f'Not found.')
                return
