from stilus.nodes.node import Node
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('/tmp/stilus.log')
formatter = logging.Formatter('[%(asctime)s] [%(name)s] '
                              '[%(levelname)s] %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


class Visitor:

    def __init__(self, root):
        self.root = root

    def visit(self, node: Node):
        if hasattr(node, 'name'):
            method = f'visit_{node.name}'
            if self.is_callable(method):
                log.debug(f'{method} is callable. {node.name}')
                return getattr(self, method)(node)
            log.info(f'{method} is NOT a callable! {node.name}')
        log.info(f'{node} has no name attribute!')
        return node

    def is_callable(self, method: str):
        methods = [f for f in dir(self) if callable(getattr(self, f))]
        if method in methods:
            return True
        return False
