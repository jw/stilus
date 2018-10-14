from stilus.nodes.node import Node


class Parser():

    def __init__(self, s, options):
        self.s = s
        self.options = options

    def parse(self) -> Node:
        return Node()
