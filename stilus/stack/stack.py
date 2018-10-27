from stilus.stack.frame import Frame


class Stack(list):

    def __init__(self):
        super().__init__()

    def __str__(self):
        buffer = []
        for frame in self:
            node = frame.block.node
            location = f'({node.filename}:{node.lineno}:{node.column})'
            if node.name == 'function':
                buffer.append(f'    at {node.name}() {location}')
            elif node.name == 'group':
                buffer.append(f'    at "{node.nodes[0].value}" {location}')
        return '\n'.join(buffer)

    def push(self, frame: Frame):
        frame.stack = self
        frame.parent = self.current_frame
        return super().append(frame)

    def current_frame(self):
        return self[self.__len__() - 1]

    def get_block_frame(self, block):
        for i in range(self.__len__()):
            if block == self[i].block:
                return self[i]

    def lookup(self, name):
        block = self.current_frame().block
        while True:
            frame = self.get_block_frame(block)
            if frame:
                return frame.lookup(name)
            block = block.parent
            if block is None:
                return
