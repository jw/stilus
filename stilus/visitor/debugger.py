import re
from os.path import dirname, abspath

from stilus import utils
from stilus.nodes.binop import BinOp
from stilus.nodes.block import Block
from stilus.nodes.boolean import Boolean
from stilus.nodes.call import Call
from stilus.nodes.expression import Expression
from stilus.nodes.function import Function
from stilus.nodes.group import Group
from stilus.nodes.ident import Ident
from stilus.nodes.literal import Literal
from stilus.nodes.media import Media
from stilus.nodes.node import Node
from stilus.nodes.property import Property
from stilus.nodes.root import Root
from stilus.nodes.selector import Selector
from stilus.nodes.string import String
from stilus.nodes.unit import Unit
from stilus.visitor.visitor import Visitor


# fixme: this method should not be called
def _handle_weird_deg_value(value, type):
    """
    Remove all numbers after the period (and the period itself) from
    deg units that have 14 zeros after the period and one single
    non-zero character at the end.

    This is a hack; it is caused by the colorsys call in the Color
    node.
    """
    result = value
    if type == 'deg' and re.match(r'[1-9]', value[-1]):
        match = re.search(r'\.(0*)', value)
        if match and len(match.groups()) == 1 and len(match.group(1)) == 14:
            result = value[:-1].rstrip('0').rstrip('.')
    return result


class Element:
    def __init__(self, type, name=None, value=None):
        self.type = type
        self.name = name
        self.value = value
        self.stuff = {}

    def __str__(self):
        return f'[{self.name}] name: {self.name}; ' \
               f'value: {self.value}; stuff: {self.stuff}'

    def __repr__(self):
        return self.__str__()


class Debugger(Visitor):

    def __init__(self, root, options):
        super().__init__(root)
        self.elements = []

    def debug(self):
        return self.visit(self.root)

    def visit_root(self, root: Root):
        self.elements = [root.debug()]
        for node in root.nodes:
            self.elements.append(self.visit(node))
        return self.elements

    def visit_block(self, block: Block):
        debug = block.debug()
        self.elements.append(debug)
        for node in block.nodes:
            self.elements.append(self.visit(node))
        return debug

    def visit_selector(self, selector: Selector):
        debug = selector.debug()
        self.elements.append(debug)
        for segment in selector.segments:
            self.elements.append(self.visit(segment))
        return debug

    def visit_keyframes(self, node: Node):
        if not node.frames:
            return

        if node.prefix == 'official':
            prefix = ''
        else:
            prefix = f'-{node.prefix}-'

        brace = '{' if self.compress else ' {\n'
        self.buf += self.out(f'@{prefix}keyframes '
                             f'{self.visit(node.value)}{brace}', node)

        self.keyframe = True
        self.indents += 1
        self.visit(node.block)
        self.indents -= 1
        self.keyframe = False

        brace = '' if self.compress else '\n'
        self.buf += self.out(f'}}{brace}')

    def visit_media(self, media: Media):
        val = media.value
        if not media.has_output() or len(val.nodes) == 0:
            return

        self.buf += self.out('@media ', media)
        self.visit(val)
        self.buf += self.out('{' if self.compress else ' {\n')
        self.indents += 1
        self.visit(media.block)
        self.indents -= 1
        self.buf += self.out('}' if self.compress else '}\n')

    def visit_querylist(self, queries):
        for i, node in enumerate(queries.nodes):
            self.visit(node)
            if len(queries.nodes) - 1 != i:
                self.buf += self.out(',' if self.compress else ', ')
                self.buf += self.out(',' if self.compress else ', ')

    def visit_query(self, node):
        length = len(node.nodes)
        if node.predicate:
            self.buf += self.out(f'{node.predicate} ')
        if node.type:
            self.buf += self.out(str(node.type) +
                                 (' and ' if length > 0 else ''))
        for i, node in enumerate(node.nodes):
            self.buf += self.out(self.visit(node))
            if length - 1 != i:
                self.buf += self.out(' and ')

    def visit_feature(self, node: Node):
        if not node.expr:
            return node.node_name
        elif node.expr.is_empty():
            return '(' + node.name + ')'
        else:
            return '(' + node.name + (':' if self.compress else ': ') + \
                   self.visit(node.expr) + ')'

    def visit_import(self, imported):
        self.buf += self.out('@import ' + self.visit(imported.path) + '\n',
                             imported)

    def visit_atrule(self, atrule):
        newline = '' if self.compress else '\n'

        self.buf += self.out(f'{self.indent()}@{atrule.type.value}', atrule)

        if atrule.value:
            self.buf += self.out(f' {atrule.value.strip()}')

        if atrule.block:
            if atrule.has_only_properties():
                self.visit(atrule.block)
            else:
                self.buf += self.out('{' if self.compress else ' {\n')
                self.indents += 1
                self.visit(atrule.block)
                self.indents -= 1
                self.buf += self.out(self.indent() + '}' + newline)
        else:
            self.buf += self.out(';' + newline)

    def visit_supports(self, node):
        if not node.has_output():
            return

        self.buf += self.out(self.indent() + '@supports ', node)
        self.is_condition = True
        self.buf += self.out(self.visit(node.condition))
        self.is_condition = False
        self.buf += self.out('{' if self.compress else '{\n')
        self.indents += 1
        self.visit(node.block)
        self.indents -= 1
        self.buf += self.out(self.indent() + ('}' if self.compress else '}\n'))

    def visit_comment(self, comment):
        return comment.debug()

    def visit_binop(self, binop: BinOp):
        debug = binop.debug()
        self.elements.append(debug)
        return debug

    def visit_function(self, fn: Function):
        debug = fn.debug()
        self.elements.append(debug)
        try:
            for node in fn.params:
                self.elements.append(self.visit(node))
        except TypeError:
            pass
        self.elements.append(self.visit(fn.block))
        return debug

    def visit_charset(self, charset):
        return '@charset ' + self.visit(charset.value) + ';'

    def visit_namespace(self, namespace):
        prefix = self.visit(namespace.prefix) + ' ' if namespace.prefix else ''
        return f'@namespace {prefix}{self.visit(namespace.val)};'

    def visit_literal(self, literal: Literal):
        return literal.debug()

    def visit_boolean(self, boolean: Boolean):
        return boolean.debug()

    def visit_rgba(self, rgba):
        return rgba.debug()

    def visit_hsla(self, hsla):
        return hsla.debug()

    def visit_unit(self, unit: Unit):
        return unit.debug()

    def visit_group(self, group: Group):
        debug = group.debug()
        self.elements.append(debug)
        try:
            for node in group.nodes:
                self.elements.append(self.visit(node))
        except TypeError:
            pass
        self.elements.append(self.visit(group.block))
        return debug

    def visit_ident(self, ident: Ident):
        debug = ident.debug()
        self.elements.append(debug)
        if ident.value is not None:
            self.elements.append(self.visit(ident.value))
        if ident.property:
            self.elements.append(self.visit(ident.property))
        return debug

    def visit_string(self, string: String):
        return string.debug()

    def visit_null(self, node: Node):
        return node.debug()

    def visit_call(self, call: Call):
        debug = call.debug()
        self.elements.append(debug)
        for node in call.args.nodes:
            self.elements.append(self.visit(node))
        return debug

    def visit_expression(self, expr: Expression):
        debug = expr.debug()
        self.elements.append(debug)
        try:
            for node in expr.nodes:
                self.elements.append(self.visit(node))
        except TypeError:
            # try:
            #     for node in iter(expr.nodes):
            #         self.elements.append(self.visit(node))
            # except TypeError:
            pass
        return debug

    def visit_arguments(self, arguments):
        debug = arguments.debug()
        self.elements.append('ARG')
        self.elements.append(debug)
        try:
            for node in arguments.nodes:
                self.elements.append(self.visit(node))
        except TypeError:
            # try:
            #     for node in iter(expr.nodes):
            #         self.elements.append(self.visit(node))
            # except TypeError:
            pass
        return debug

    def visit_property(self, property: Property):
        debug = property.debug()
        self.elements.append(debug)
        self.elements.append(self.visit(property.expr))
        return debug
