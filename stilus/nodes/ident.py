from .null import Null


class Ident:

    def __init__(self, name, value, mixin):
        self.name = name
        self.value = value if value else Null
        self.mixin = mixin

