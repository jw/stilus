from typing import Type

from stilus.nodes.ident import Ident
from stilus.nodes.node import Node


class Scope:

    def __init__(self):
        self.commons = {}

    def __hash__(self):
        return hash(self.commons)

    def __eq__(self, other):
        if isinstance(other, Scope):
            return self.commons == other.commons
        return False

    def __str__(self):
        if not self.commons:
            return '[Empty scope]'
        else:
            commons = ', '.join(f'@{key}' for key in self.commons.keys())
            return f'[Scope {commons}]'

    def __repr__(self):
        return self.__str__()

    def add(self, ident: Ident):
        """Add ident node to the current scope."""
        self.commons[ident.string] = ident.value

    def lookup(self, name) -> Type[Node]:
        """Lookup the given local variable name.
        :param name:
        :return:
        """
        # print(f'SCOPE: Lookup of {str(name)} in {str(list(self.commons))}.')
        return self.commons.get(str(name), None)
