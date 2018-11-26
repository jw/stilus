
class Scope:

    def __init__(self):
        self.commons = {}

    def __hash__(self):
        return hash(self.commons)

    def __eq__(self, other):
        if isinstance(other, Scope):
            return self.commons == other.commons
        return False

    def add(self, ident):
        self.commons[ident.string] = ident.value

    def lookup(self, name):
        return self.commons.get(name, None)
