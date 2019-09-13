import re
from os.path import dirname, abspath

from stilus import utils
from stilus.nodes.block import Block
from stilus.nodes.boolean import Boolean
from stilus.nodes.call import Call
from stilus.nodes.expression import Expression
from stilus.nodes.group import Group
from stilus.nodes.ident import Ident
from stilus.nodes.media import Media
from stilus.nodes.node import Node
from stilus.nodes.property import Property
from stilus.nodes.root import Root
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


class Compiler(Visitor):

    def __init__(self, root, options):
        super().__init__(root)
        self.compress = options.get('compress', False)
        self.linenos = options.get('linenos', False)
        self.spaces = options.get('indent spaces', 2)
        self.indents = 0
        self.buf = None
        self.last = None
        self.keyframe = None
        self.is_condition = None
        self.is_url = None
        self.stack = []

    def compile(self):
        return self.visit(self.root)

    def out(self, string, node=None):
        return string

    def indent(self):
        if self.compress:
            return ''
        return ' ' * (self.spaces * self.indents)

    def need_brackets(self, node):
        if 1 == self.indents:
            return True
        if 'atrule' != node.node_name:
            return True
        if node.has_only_properties():
            return True
        return False

    def visit_root(self, root: Root):
        self.buf = ''
        for node in root.nodes:
            if self.linenos:
                self.debug_info(node)
            ret = self.visit(node)
            if ret:
                self.buf += self.out(ret + '\n', node)
        return self.buf

    def visit_block(self, block: Block):
        if self.compress:
            separator = ''
        else:
            separator = '\n'

        if block.has_properties() and not block.lacks_rendered_selectors:

            last_property_index = -1
            if self.compress:
                for i, node in enumerate(block.nodes):
                    if node.name == 'property':
                        last_property_index = i
                        break

            needs_brackets = self.need_brackets(block.node)
            if needs_brackets:
                self.buf += self.out('{' if self.compress else ' {\n')
                self.indents += 1

            for i, node in enumerate(block.nodes):
                self.last = last_property_index == i
                if node.node_name in ['null', 'expression', 'function',
                                      'group', 'block', 'unit', 'media',
                                      'keyframes', 'atrule', 'supports']:
                    continue
                elif node.node_name == 'comment' and node.inline and \
                        not self.compress:
                    self.buf = self.buf[0:-1]
                    self.buf += self.out(f' {self.visit(node)}\n', node)
                elif node.node_name == 'property':
                    ret = self.visit(node) + separator
                    self.buf += ret if self.compress else self.out(ret, node)
                else:
                    self.buf += self.out(self.visit(node) + separator, node)

            if needs_brackets:
                self.indents -= 1
                self.buf += self.out(self.indent() + '}' + separator)

        # nesting
        for node in block.nodes:
            if node.node_name in ['group', 'block', 'keyframes']:
                if self.linenos:
                    self.debug_info(node)
                self.visit(node)
            elif node.node_name in ['media', 'import', 'atrule', 'supports']:
                self.visit(node)
            elif node.node_name == 'comment':
                if not node.suppress:
                    self.buf += self.out(self.indent() +
                                         self.visit(node) + '\n', node)
            elif node.node_name in ['charset', 'literal', 'namespace']:
                self.buf += self.out(self.visit(node) + '\n', node)

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
        if self.compress:
            if comment.suppress:
                return ''
            else:
                return comment.value
        else:
            return comment.value

    def visit_function(self, fn):
        return fn.function_name

    def visit_charset(self, charset):
        return '@charset ' + self.visit(charset.value) + ';'

    def visit_namespace(self, namespace):
        prefix = self.visit(namespace.prefix) + ' ' if namespace.prefix else ''
        return f'@namespace {prefix}{self.visit(namespace.value)};'

    def visit_literal(self, literal):
        val = literal.value
        if literal.css:
            val = re.sub(r'^  ', val, flags=re.MULTILINE)
        return val

    def visit_boolean(self, boolean: Boolean):
        return str(boolean)

    def visit_rgba(self, rgba):
        return str(rgba)

    def visit_hsla(self, hsla):
        return str(hsla.rgba())

    def visit_unit(self, unit: Unit):
        t = unit.type if unit.type else ''
        n = unit.value
        f = isinstance(n, float)
        if self.compress:
            # always return '0' unless the unit is a percentage or time
            if '%' != t and 's' != t and 'ms' != t and 0 == n:
                return 0
            if f:
                # remove trailing zeros
                n = f'{self.a:.3f}'.rstrip('0').rstrip('.')
                if 1 > float(n) > -1:
                    # omit leading '0' on floats
                    n = n.replace('0.', '.')
                return n
        if f:
            v = f'{n:.15f}'.rstrip('0').rstrip('.')
            v = _handle_weird_deg_value(v, t)
            return f'{v}{t}'
        else:
            return f'{n}{t}'

    def visit_group(self, group: Group):
        if self.keyframe:
            stack = []
        else:
            stack = self.stack

        if self.compress:
            comma = ','
        else:
            comma = ',\n'

        stack.append(group.nodes)

        # selectors
        if group.block.has_properties():
            selectors = utils.compile_selectors(stack, indent=self.indent())

            if selectors:
                if self.keyframe:
                    if self.compress:
                        comma = ','
                    else:
                        comma = ', '

                for i, selector in enumerate(selectors):
                    last = i == len(selectors) - 1

                    # keyframe bocks (10%, 20% { ... })
                    # checkme: if (this.keyframe)
                    # checkme:   selector = i ? selector.trim() :
                    # checkme:                   selector;
                    if self.keyframe:
                        selector.strip()

                    self.buf += self.out(selector + ('' if last else comma),
                                         group.nodes[i])
            else:
                group.block.lacks_rendered_selectors = True

        self.visit(group.block)
        stack.pop()

    def visit_ident(self, ident: Ident):
        return ident.name

    def visit_string(self, string: String):
        return string.value if self.is_url else str(string)

    def visit_null(self, node: Node):
        return ''

    def visit_call(self, call: Call):
        self.is_url = 'url' == call.function_name
        args = [self.visit(node) for node in call.args.nodes]
        if self.compress:
            args = ','.join(args)
        else:
            args = ', '.join(args)
        if self.is_url:
            args = f'"{args}"'
        self.is_url = False
        return f'{call.function_name}({args})'

    def visit_expression(self, expr: Expression):
        buf = []
        length = len(expr.nodes)
        nodes = [self.visit(node) for node in expr.nodes]

        for i, (node, next) in enumerate(zip(nodes, nodes[1:] + ['end'])):
            last = i == length - 1
            buf.append(str(node))
            if '/' == next or '/' == node:
                continue
            if last:
                continue

            if self.is_url or (self.is_condition and
                               (')' == next or '(' == node)):
                space = ''
            else:
                space = ' '

            if expr.is_list:
                if self.compress:
                    buf.append(',')
                else:
                    buf.append(', ')
            else:
                buf.append(space)

        return ''.join(buf)

    def visit_arguments(self, arguments):
        return self.visit_expression(arguments)

    def visit_property(self, property: Property):
        val = self.visit(property.expr).strip()
        if property.name:
            name = property.name
        else:
            name = ''.join(property.segments)
        arr = []
        arr.append(self.out(self.indent()))
        arr.append(self.out(name + (':' if self.compress else ': ')))
        arr.append(self.out(val, property.expr))
        if self.last:
            separator = ''
        else:
            separator = ';'
        arr.append(self.out(separator if self.compress else ';'))
        return ''.join(arr)

    def debug_info(self, node: Node):
        if node.filename == 'stdin':
            path = 'stdin'
        else:
            path = dirname(abspath(node.filename))
        line = node.nodes[0].lineno if node.nodes else node.lineno
        if self.linenos:
            self.buf += f'\n/* line {line} : {path} */\n'
