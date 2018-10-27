from stilus.nodes.node import Node


class Visitor:

    def __init__(self, root):
        self.root = root

    def visit(self, node: Node):
        method = f'visit{node.name}'
        if self.is_callable(method):
            return self.method(node)
        return node

    def is_callable(self, method: str):
        methods = [func for func in dir(self) if callable(getattr(self, func))]
        if method in methods:
            return True
        return False
