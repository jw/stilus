from stilus.nodes.node import Node


class Boolean(Node):

    def __init__(self, value):
        super().__init__(value)

    def __str__(self):
        return f'{self.name}: {self.value}'

    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':
    print(Boolean(True))
    print(Boolean(False))
    print(Boolean(True is False))
