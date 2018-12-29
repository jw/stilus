from stilus.nodes.node import Node

# import logging

# log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)
# fh = logging.FileHandler('/tmp/stilus.log')
# formatter = logging.Formatter('[%(asctime)s] [%(node_name)s] '
#                               '[%(levelname)s] %(message)s')
# fh.setFormatter(formatter)
# log.addHandler(fh)


class Visitor:

    def __init__(self, root):
        self.root = root

    def visit(self, node: Node):
        if hasattr(node, 'node_name'):
            method = f'visit_{node.node_name}'
            if self.is_callable(method):
                print(f'{method} is callable. [{node.node_name}]')
                return getattr(self, method)(node)
            else:
                print(f'{method} is NOT a callable! [{node.node_name}]')
        else:
            print(f'{type(node)} has no node_name attribute!')
        print(f'returning {type(node)}')
        return node

    def is_callable(self, method: str):
        methods = [f for f in dir(self) if callable(getattr(self, f))]
        if method in methods:
            return True
        return False
