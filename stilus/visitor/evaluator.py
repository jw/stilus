import os
import re
from distutils import dirname

from stilus import utils, colors
from stilus.nodes.block import Block
from stilus.nodes.color import RGBA
from stilus.nodes.expression import Expression
from stilus.nodes.function import Function
from stilus.nodes.group import Group
from stilus.nodes.ident import Ident
from stilus.nodes.import_node import Import
from stilus.nodes.literal import Literal
from stilus.nodes.null import null
from stilus.nodes.object_node import ObjectNode
from stilus.nodes.string import String
from stilus.parser import Parser, ParseError
from stilus.stack.frame import Frame
from stilus.stack.stack import Stack
from stilus.visitor.visitor import Visitor


class Evaluator(Visitor):

    def __init__(self, root, options: dict):
        super().__init__(root)
        self.options = options
        self.functions = options.get('functions', {})
        self.stack = Stack()
        self.imports = options.get('imports', {})
        self.commons = options.get('globals', {})
        self.paths = options.get('paths', [])
        self.prefix = options.get('prefix', '')
        self.filename = options.get('filename', None)
        self.include_css = options.get('include css', False)
        self.resolve_url = self.functions.url and \
            'resolver' == self.functions.url.name and \
            self.functions.url.options
        self.paths.push(dirname(options.get('filename', __file__)))
        self.common = Frame(root)
        self.stack.push(self.common)
        self.warnings = options('warn', False)
        self.calling = []  # todo: remove, use stack
        self.import_stack = []
        self.require_history = {}
        self.result = 0
        self.current_block = None

    def import_file(self, node: Import, file, literal):
        import_stack = self.import_stack

        # handling 'require'
        if node.once:
            if self.require_history[file]:
                return null
            self.require_history[file] = True

            if literal and not self.include_css:
                return node

        # avoid overflows from reimporting the same file
        if file in import_stack:
            raise ImportError('import loop has been found')

        with open(file) as f:
            source = f.read()

        # shortcut for empty files
        if not source.strip():
            return null

        # expose imports
        node.path = file
        node.dirname = dirname(file)
        # store modified time
        node.mtime = os.stat(file).st_mtime
        self.paths.append(node.dirname)

        if '_imports' in self.options:
            self.options['_imports'].append(node.clone())

        # parse the file
        import_stack.append(file)
        # todo: nodes.filename = file

        if literal:
            re.sub('\n\n?', '\n', source)
            literal = Literal(source)
            literal.lineno = 1
            literal.column = 1
            if not self.resolve_url:
                return literal

        # parse
        block = Block()
        parser = Parser(source, utils.merge({'root': block}, self.options))

        try:
            block = parser.parse()
        except Exception:
            line = parser.lexer.lineno
            column = parser.lexer.column
            if literal and self.include_css and self.resolve_url:
                self.warn(f'ParseError: {file}:{line}:{column}. '
                          f'This file is included as-is')
                return literal
            else:
                raise ParseError(file, line, column, source)

        # evaluate imported 'root'
        block = block.clone(self.current_block)
        block.parent = self.current_block
        block.scope = False
        ret = self.visit(block)
        import_stack.pop()

        if not self.resolve_url or not self.resolve_url:
            self.paths.pop()

        return ret

    def visit(self, node):
        try:
            super().visit(node)
        except Exception as e:
            if e.filename:
                raise e
            try:
                with open(e.filename) as f:
                    e.input = f.read()
            except Exception:
                pass
            raise ParseError(filename=e.filename, lineno=node.lineno,
                             column=node.column, input=e.input)

    def setup(self):
        root = self.root
        imports = []

        self.populate_global_scope()
        for file in self.imports:
            expr = Expression()
            expr.push(String(file))
            imports.push(Import(expr))

        root.nodes.insert(imports)

    def populate_global_scope(self):
        scope = self.common.scope()

        # colors
        for color, value in colors.items():
            rgba = RGBA(value[0], value[1], value[2], value[3])
            ident = Ident(color, rgba)
            rgba.value = color
            scope.add(ident)

        # todo: also expose url javascript function; might be hard >8-(
        scope.add(Ident('embedurl', Function('embedurl', None, None)))

        # user defined globals
        commons = self.commons
        for common, val in commons.items():
            if val.name:
                scope.add(Ident(common, val))

    def evaluate(self):
        self.setup()
        return self.visit(self.root)

    def visit_group(self, group: Group):
        group.nodes = map(self.interpolate, group.nodes)
        group.block = self.visit(group.block)
        return group

    def visist_return(self, ret):
        ret.expr = self.visit(ret.expr)
        raise ret

    def visit_media(self, media):
        media.block = self.visit(media.block)
        media.val = self.visit(media.val)
        return media

    def visit_queryList(self, queries):
        for node in queries.nodes:
            self.visit(node)

        if len(queries.nodes) == 1:
            query = queries.nodes[0]
            val = self.lookup(query.type)
            if val:
                val = val.first().string
                if not val:
                    return queries
                parser = Parser(val, self.options)
                queries = self.visit(parser.queries())

        return queries

    def visit_query(self, node):
        node.predicate = self.visit(node.predicate)
        node.type = self.visit(node.type)
        for n in node.nodes:
            self.visit(n)
        return node

    def visit_feature(self, node):
        node.name = self.interpolate(node)
        if node.expr:
            self.result += 1
            node.expr = self.visit(node.expr)
            self.result -= 1
        return node

    def visit_object(self, obj: ObjectNode):
        for key, value in obj.values.items():
            obj.values[key] = self.visit(value)
        return obj

    def visit_member(self, node):
        left = node.left
        right = node.right
        obj = self.visit(left).first()

        if 'object' != obj.name:
            raise ParseError(f'{left} has no property .{right}')

        if node.value:
            self.result += 1
            # checkme: this can not ever work - what is set?
            obj.set(right.value, self.visit(node.value))
            self.result -= 1

        # checkme: what is get?
        return obj.get(right.value)

    def interpolate(self, node):
        is_selector = 'stmt_selector' == node.name

        def to_string(node):
            if node.name in ['function', 'ident']:
                return node.value
            elif node.name in ['literal', 'string']:
                # huh?
                if self.prefix and not node.prefixed and not node.value.name:
                    node.val = re.sub(r'\.', f'.{self.prefix}', node.val)
                    node.prefixed = True
                return node.value
            elif node.name == 'unit':
                # interpolation inside keyframes
                return f'{node.value}%' if '%' == node.type else node.value
            elif node.name == 'member':
                return to_string(self.visit(node))
            elif node.name == 'expression':
                # prevent cyclic 'stmt_selector()' calls
                if self.calling and 'stmt_selector' in self.calling and \
                        self._selector:
                    return self.selector
                self.result += 1
                ret = to_string(self.visit(node).first())
                if is_selector:
                    self._selector = ret
                return ret

        if node.segments:
            return ''.join(map(to_string, node.segments))
        else:
            return to_string(node)
