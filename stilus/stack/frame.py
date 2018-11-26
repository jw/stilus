from stilus.nodes.block import Block
from stilus.nodes.null import null
from stilus.stack.scope import Scope


# todo: create getter and setter for scope or at least clean this up!
class Frame:

    def __init__(self, block: Block, parent: Block = None):
        if callable(getattr(block, 'scope', None)):
            self._scope = null if block.scope is False else Scope()
        else:
            self._scope = Scope()
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

    def set_scope(self, scope: Scope):
        self._scope = scope

    def lookup(self, name):
        if self._scope:
            return self._scope.lookup(name)
        return None
