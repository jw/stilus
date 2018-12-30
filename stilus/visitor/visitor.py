from stilus.nodes.node import Node

import logging
# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)


class Visitor:

    def __init__(self, root):
        self.root = root

    def visit(self, node: Node):
        """Visit a method based on the node's type.  For example when the
        bode has a node_name == 'block', the method visit_block(node)
        will be called.
        :param node: The node who's type will be used to visit a method.
        :return: the node if its type does not have a method, or the
        return value of the visited method.
        """

        if hasattr(node, 'node_name'):
            method = f'visit_{node.node_name}'
            if self.is_callable(method):
                log.debug(f'{method} is callable. [{node.node_name}]')
                return getattr(self, method)(node)

            # debug else
            if log.isEnabledFor(logging.DEBUG) and self.is_callable(method):
                log.debug(f'{method} is NOT a callable! [{node.node_name}]')

        # debug else
        if log.isEnabledFor(logging.DEBUG) and not hasattr(node, 'node_name'):
            log.debug(f'{type(node)} has no node_name attribute!')

        log.debug(f'returning {type(node)}')
        return node

    def is_callable(self, method: str):
        methods = [f for f in dir(self) if callable(getattr(self, f))]
        if method in methods:
            return True
        return False
