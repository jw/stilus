from deprecated import deprecated

from stilus.nodes.block import Block
from stilus.stack.scope import Scope


# todo: create getter and setter for scope or at least clean this up!
class Frame:

    def __init__(self, block: Block, parent: Block = None):
        if hasattr(block, 'scope') and block.scope is False:
            self._scope = None
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

    def __str__(self):
        if hasattr(self.block, 'scope') and self.block.scope is False:
            scope = 'scope-less'
        else:
            scope = f'{self.scope()}'
        return f'[Frame {scope}]'

    def __repr__(self):
        return self.__str__()

    def scope(self):
        """Return this frame's scope or the parent scope
        for scope-less blocks.
        :return:
        """
        if self._scope:
            return self._scope
        try:
            # print(f'{self.parent}; type: {type(self.parent)}')
            return self.parent.scope()
        except AttributeError:
            raise TypeError('Cannot read property \'scope\' of undefined')

    @deprecated
    def set_scope(self, scope: Scope):
        self._scope = scope

    def lookup(self, name):
        """
        Lookup the given local variable `name`.
        :param name:
        :return:
        """
        # print(f'FRAME: Lookup of {name} in {self.scope()}...')
        return self.scope().lookup(name)
