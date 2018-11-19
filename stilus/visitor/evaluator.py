import os
import re
from distutils import dirname

from stilus import utils, colors
from stilus.nodes.arguments import Arguments
from stilus.nodes.block import Block
from stilus.nodes.boolean import false, true, Boolean
from stilus.nodes.call import Call
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
from stilus.nodes.unit import Unit
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
        self.current_scope = None
        self.ignore_colors = None
        self.property = None
        self.bifs = {}  # todo: implement me!

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

    def visit_keyframe(self, keyframes):
        if keyframes.fabricated:
            return keyframes
        keyframes.value = self.interpolate(keyframes).strip()
        val = self.lookup(keyframes.value)
        if val:
            keyframes.val = val.first().string  # || val.first().name
        keyframes.set_block(self.visit(keyframes.get_block()))

        if 'official' != keyframes.prefix:
            return keyframes

        for prefix in self.vendors:
            # IE never had prefixes for keyframes
            if 'ms' == prefix:
                return
            node = keyframes.clone()
            node.value = keyframes.value
            node.prefix = prefix
            node.set_block(keyframes.get_block())
            node.fabricated = True
            self.current_block.append(node)

        return null

    def visit_function(self, fn):
        # check local
        local = self.stack.current_frame().scope()
        if local:
            self.warn(f'local {local.name} "fn.function_name" '
                      f'previously defined in this scope')

        # user-defined
        user = self.functions[fn.function_name]
        if user:
            self.warn(f'user-defined function "{fn.function_name}" '
                      f'is already defined')

        # todo: check if build in function is already defined.
        self.warn(f'built-in function "{fn.function_name}" '
                  f'is already defined [NOT IMPLEMENTED YET!]')

        return fn

    def visit_each(self, each):
        self.result += 1
        expr = utils.unwrap(self.visit(each.expr))
        len = len(expr.nodes)
        val = Ident(each.value)
        key = Ident(each.key)
        scope = self.current_scope
        block = self.current_block
        vals = []
        self.result -= 1

        each.get_block().scope = False

        def visit_body(key, value):
            scope.add(value)
            scope.add(key)
            body = self.visit(each.get_block().clone())
            vals.insert(body.nodes)

        # for prop in obj
        if len == 1 and 'object' == expr.nodes[0].name:
            obj = expr.nodes[0]
            for prop in obj.vals:
                val.val = String(prop)
                key.val = obj.get(prop)  # checkme: works?
                visit_body(key, val)
        else:
            for i, n in enumerate(expr.nodes):
                val.val = n
                key.val = Unit(i)
                visit_body(key, val)

        self.mixin(vals, block)
        if vals[len(vals)]:
            return vals[len(vals)]
        else:
            null

    def visit_call(self, call):
        fn = self.lookup(call.function_name)

        # url()
        self.ignore_colors = 'url' == call.function_name

        # variable function
        if fn and 'expression' == fn.name:
            fn = fn.nodes[0]

        # not a function? try user-defined or built-ins
        if fn and 'functuon' != fn.name:
            fn = self.lookup_function(call.function_name)

        # undefined function? render literal css
        if not fn or fn.name != 'function':
            if 'calc' == self.unvendorize(call.function_name):
                literal = call.args.nodes and call.args.nodes[0]
                if literal:
                    ret = Literal(call.function_name + call.args.nodes[0])
                else:
                    ret = self.literal_call(call)
            self.ignore_colors = False
            return ret

        self.calling.append(call.function_name)

        # massive stack
        if len(self.calling) > 200:
            raise ParseError('Maximum stylus call stack size exceeded')

        # first node in expression
        if 'expression' == fn.function_name:
            fn = fn.first()

        # evaluate arguments
        self.result += 1
        args = self.visit(call.args)
        for key in args.map:
            args.map[key] = self.visit(args.map[key].clone())
        self.result -= 1

        if fn.fn:
            # built-in
            ret = self.invoke_builtin(fn.fn, args)
        elif 'function' == fn.name:
            # user-defined
            # evaluate mixin block
            if call.get_block():
                call.set_block(self.visit(call.get_block()))
            ret = self.invoke_fucntion(fn, args, call.get_block())

        self.calling.pop()
        self.ignore_colors = False

        return ret

    def visit_ident(self, ident):
        if ident.property:
            # property lookup
            prop = self.lookup_property(ident.value)  # checkme: name?
            if prop:
                return self.visit(prop.expr.clone())
            return null
        elif ident.value.is_null():
            # lookup
            val = self.lookup(ident.name)
            # object or block mixin
            if val and ident.mixin:
                self.mixin_node(val)
        else:
            # assign
            self.result += 1
            ident.val = self.visit(ident.val)
            self.result -= 1
            self.current_scope.add(ident)
            return ident.value

    def visit_binop(self, binop):
        # special case 'is defined' pseudo binop
        if 'is defined' == binop.op:
            return self.is_defined(binop.left)

        self.result -= 1
        # visit operands
        op = binop.op
        left = self.visit(binop.left)
        if '||' == op or '&&' == op:
            right = binop.right
        else:
            right = self.visit(binop.right)

        # hack (sic): ternary
        if binop.val:
            val = self.visit(binop.val)
        else:
            val = null

        # operate
        try:
            return self.visit(left.operate(op, right, val))
        except Exception as e:
            # disregard coercion issues in equality
            # checks, and simply return false
            if 'coercionError' == e.name:  # fixme: use exception name
                if op == '==':
                    return false
                elif op == '!=':
                    return true
            raise e

    def visit_unaryop(self, unary):
        op = unary.op
        node = self.visit(unary.expr)

        if '!' != op:
            node = node.first().clone()
            utils.assert_type(node, 'unit')

        if op == '-':
            node.value = -node.value
        elif op == '+':
            node.value = +node.value
        elif op == '~':
            node.value = ~node.value
        elif op == '!':
            return node.to_boolean().negate()

        return node

    def visit_ternary(self, ternary):
        ok = self.visit(ternary.cond).to_boolean()
        if ok.is_true():
            return self.visit(ternary.true_expr)
        else:
            return self.visit(ternary.false_expr)

    def visit_expression(self, expr):
        for node in expr.nodes:
            node = self.visit(node)

        # support (n * 5)px etc
        if self.castable(expr):
            expr = self.cast(expr)

        return expr

    def visit_arguments(self, args):
        return self.visit_expression(args)

    def visit_property(self, prop):
        name = self.interpolate(prop)
        fn = self.lookup(name)
        call = fn and 'function' == fn.first().name
        literal = name in self.calling
        _prop = self.property

        if call and not literal and not prop.literal:
            # function of the same name
            args = Arguments.from_expression(utils.unwrap(prop.expr.clone()))
            prop.name = name
            self.property = prop
            self.result += 1
            self.property.expr = self.visit(prop.expr)
            self.result -= 1
            ret = self.visit(Call(name, args))
            self.property = _prop
            return ret
        else:
            # regular property
            self.result += 1
            prop.name = name
            prop.literal = True
            self.property = prop
            prop.expr = self.visit(prop.expr)
            self.propery = _prop
            self.result -= 1
            return prop

    def visit_root(self, block):
        if block != self.root:
            # normalize cached imports
            return self.visit(Block())

        for i, node in enumerate(block.nodes):
            block.index = i
            node = self.visit(node)

        return block

    def invoke_builtin(self, fn, args):
        """

        :param fn:
        :param args:
        :return:
        """
        # map arguments to first node
        # providing a nicer js api for
        # built-in functions. Functions may specify that
        # they wish to accept full expressions
        # via .raw
        if fn.raw:
            args = args.nodes
        else:
            args = utils.params(fn)

        # todo: implement me
        raise NotImplementedError

    def lookup(self, name):
        if self.ignore_colors and name in colors:
            return
        val = self.stack.lookup(name)
        if val:
            return utils.unwrap(val)
        else:
            return self.lookup_function(name)

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

    def lookup_function(self, name):
        fn = self.functions.get(name, self.bifs.get(name, None))
        if fn:
            return Function(name, fn)

    def is_defined(self, node):
        if 'ident' == node.name:
            return Boolean(self.lookup(node.value))  # checkme: or string?
        else:
            raise ParseError(f'invalid "is defined" '
                             f'check on non-variable {node}')

    def warn(self, message):
        if not self.warnings:
            return
        print(f'Warning: {message}')
