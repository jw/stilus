from stilus.nodes.node import Node

import logging
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

        method = None
        if hasattr(node, 'node_name'):
            method = f'visit_{node.node_name}'
            # log.info(f'Visiting {method}({node.node_name}).')
            if self.callable(method):
                log.debug(f'{method} is callable. [{node.node_name}]')
                return getattr(self, method)(node)

            # debug else
            if log.isEnabledFor(logging.DEBUG) and not self.callable(method):
                log.debug(f'{method} is NOT a callable! [{node.node_name}]')

        # debug else
        if log.isEnabledFor(logging.DEBUG) and not hasattr(node, 'node_name'):
            log.debug(f'{type(node)} has no node_name attribute!')

        if method:
            log.info(f'Returning {type(node)} from '
                     f'{method}({node.node_name}).')
        else:
            log.info(f'Skipping, since no visiting method found for {node}.')
        return node

    def callable(self, method: str):
        methods = [f for f in dir(self) if callable(getattr(self, f))]
        if method in methods:
            return True
        return False
