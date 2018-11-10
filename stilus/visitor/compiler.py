from stilus.nodes.block import Block
from stilus.nodes.expression import Expression
from stilus.nodes.group import Group
from stilus.nodes.ident import Ident
from stilus.nodes.property import Property
from stilus.nodes.root import Root
from stilus.visitor.visitor import Visitor


class Compiler(Visitor):

    def __init__(self, root, options):
        self.root = root
        self.options = options
        self.buf = None
        self.indents = 1

    def indent(self):
        return '  ' * self.indents

    def need_brackets(self, node):
        return True

    def compile(self):
        return self.visit(self.root)

    def visitRoot(self, root: Root):
        self.buf = ''
        for node in root.nodes:
            ret = self.visit(node)
            if ret:
                self.buf += self.out(ret + '\n', node)
        return self.buf

    def visitGroup(self, group: Group):
        self.buf += group.nodes[0].segments[0].value
        self.visit(group.nodes[0].block)

    def visitBlock(self, block: Block):
        separator = '\n'
        if block.has_properties():
            needs_brackets = self.need_brackets(block.node)
            if needs_brackets:
                self.buf += self.out(' {\n')
                self.indents += 1
            for node in block.nodes:
                if node.name == 'property':
                    ret = self.visit(node) + separator
                    self.buf += self.out(ret, node)
            if needs_brackets:
                self.indents -= 1
                self.buf += self.out('}' + separator)

    def visitProperty(self, property: Property):
        return f'  {property.segments[0].string}: ' \
               f'{property.expr.nodes[0].string}'

    def visitExpression(self, expression: Expression):
        buf = []
        nodes = [self.visit(node) for node in expression.nodes]
        for node in nodes:
            buf.append(node)

    def visitIdent(self, ident: Ident):
        return ident.value

    def out(self, string, node=None):
        return string
