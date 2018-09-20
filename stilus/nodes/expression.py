from stilus.nodes.node import Node


class Expression(Node):

    def __init__(self):
        self.nodes = []

    def push(self, node):
        self.nodes.append(node)


