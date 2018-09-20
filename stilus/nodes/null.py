
class Null:

    def __init__(self):
        self.data = {'isNull': True, 'hash': None}

    def __str__(self):
        return 'null'

    def __repr__(self):
        return str(self)

    def __bool__(self):
        return False

    def __getattr__(self, attr):
        return self.data[attr]
