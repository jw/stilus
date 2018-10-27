
class Scope:

    def __init__(self):
        self.locals = {}

    def __hash__(self):
        return hash(self.locals)

    def __eq__(self, other):
        if isinstance(other, Scope):
            return self.locals == other.locals
        return False

    def add(self, ident):
        self.locals[ident.string] = ident.value

    def lookup(self, name):
        return self.locals.get(name, None)
