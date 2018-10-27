from stilus.nodes.block import Block
from stilus.stack.scope import Scope


class Frame:

    def __init__(self, block: Block, parent: Block=None):
        self._scope = None if block.scope is False else Scope()
        self.block = block
        self.parent = parent

    def __key(self):
        return self._scope, self.block, self.parent

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Frame):
            return self.__key() == other.__key()
        return False

    def scope(self):
        if self._scope:
            return self._scope
        elif self.parent:
            return self.parent.scope
        return None

    def lookup(self, name):
        if self._scope:
            return self._scope.lookup(name)
        return None
