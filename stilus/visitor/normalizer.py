import re
from collections import defaultdict

from stilus import utils
from stilus.nodes.block import Block
from stilus.nodes.group import Group
from stilus.nodes.literal import Literal
from stilus.nodes.node import Node
from stilus.nodes.null import null
from stilus.nodes.root import Root
from stilus.nodes.selector import Selector
from stilus.visitor.visitor import Visitor


class Normalizer(Visitor):

    def __init__(self, root, options):
        super().__init__(root)
        self.hoist = options.get('hoist atrules', False)
        self.stack = []
        self.selector_map = defaultdict(list)
        self.imports = []
        self.charset = None
        self.root_index = 0

    def normalize(self):
        ret = self.visit(self.root)
        if self.hoist:
            # hoist @import
            if len(self.imports) > 0:
                ret.nodes = self.imports.insert(ret.nodes)
            # hoist @charset
            if self.charset:
                ret.nodes = self.charset.insert(ret.nodes)
        return ret

    def bubble(self, node: Node):
        props = []
        others = []

        def filter_props(block):
            for node in block.nodes:
                node = self.visit(node)
                if node.node_name == 'property':
                    props.append(node)
                elif node.node_name == 'block':
                    filter_props(node)
                else:
                    others.append(node)

        filter_props(node.block)

        if props:
            selector = Selector([Literal('&')])
            selector.lineno = node.lineno
            selector.column = node.column
            selector.filename = node.filename
            selector.value = '&'

            group = Group()
            group.lineno = node.lineno
            group.column = node.column
            group.filename = node.filename

            block = Block(node.block, group)
            block.lineno = node.lineno
            block.column = node.column
            block.filename = node.filename

            for prop in props:
                block.append(prop)

            group.append(selector)
            group.block = block

            node.block.nodes = []
            node.block.append(group)
            for other in others:
                node.block.append(other)

            group = self.closest_group(node.block)
            if group:
                node.group = group.clone()

            node.bubbled = True

    # fixme: this is a terrible conversion form stylus
    def closest_group(self, block: Block) -> Group:
        parent = block.parent
        while parent and parent.node:
            node = parent.node
            if node.node_name == 'group':
                return node
            if not node.block:
                parent = False
            if not node.block.parent:
                parent = False
            parent = node.block.parent

    def visit_root(self, block):
        ret = Root()
        for node in block.nodes:
            if node.node_name in ['null', 'expression', 'function',
                                  'unit', 'atblock']:
                continue
            else:
                self.root_index = 1
                ret.append(self.visit(node))
        return ret

    def visit_property(self, property):
        self.visit(property.expr)
        return property

    def visit_expression(self, expression):
        visited = []
        for node in expression.nodes:
            if node.node_name == 'block':
                literal = Literal('block')
                literal.lineno = node.lineno
                literal.column = node.column
                visited.append(literal)
            else:
                visited.append(node)
        return visited

    def visit_block(self, block):
        if block.has_properties():
            for node in block.nodes:
                if block.node_name in ['null', 'expression', 'function',
                                       'group', 'unit', 'atblock']:
                    continue
                else:
                    node = self.visit(node)

        # nesting
        for node in block.nodes:
            node = self.visit(node)

        return block

    def visit_group(self, group):
        stack = self.stack
        normalized = []
        for selector in group.nodes:
            # do nothing
            if ',' not in selector.value:
                normalized = group.nodes
                break
            # replace '\,' with ','
            if '\\' in selector.value:
                re.sub(r'\\,', ',')
                normalized = group.nodes
                break
            parts = selector.value.split(',')
            root = True if selector.value[0] == '/' else False
            for i, part in enumerate(parts):
                part = part.trim()
                if root and '&' not in part:
                    part = '/' + part
                s = Selector([Literal(part)])
                s.value = part
                s.block = group.get_block()
                normalized[i] = s
        stack.append(normalized)

        selectors = utils.compile_selectors(stack, True)

        # add selectors for lookup
        for selector in selectors:
            self.selector_map[selector].append(group)

        # extensions
        self.extend(group, selectors)

        stack.pop()
        return group

    def visit_function(self, function):
        return null

    def visit_media(self, media):
        # medias = []
        # group = self.closest_group(media.block)

        def merge_queries(block):
            for node in block.nodes:
                if node.node_name == 'media':
                    node.value = media.value.merge

    def extend(self, group, selectors):
        pass
