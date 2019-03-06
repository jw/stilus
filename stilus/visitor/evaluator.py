import logging
import os
import re
from distutils import dirname
from pathlib import Path

from stilus import utils
from stilus.colors import colors
from stilus.nodes.arguments import Arguments
from stilus.nodes.block import Block
from stilus.nodes.boolean import Boolean
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
from stilus.stack.scope import Scope
from stilus.stack.stack import Stack
from stilus.units import units
from stilus.visitor.visitor import Visitor

log = logging.getLogger(__name__)


class Evaluator(Visitor):

    def __init__(self, root, options: dict):
        super().__init__(root)
        self.options = options
        self.functions = options.get('functions', {})
        self.stack = Stack()
        self.imports = options.get('imports', [])
        self.commons = options.get('globals', {})
        self.paths = options.get('paths', [])
        self.prefix = options.get('prefix', '')
        self.filename = options.get('filename', None)
        self.include_css = options.get('include css', False)

        self.resolve_url = False
        if 'url' in self.functions:
            url = self.functions['url']
            if url.name == 'resolver' and url.options:
                self.resolve_url = True

        filename = Path(options.get('filename', '.'))
        self.paths.append(str(filename.parent))

        self.common = Frame(root)
        self.stack.append(self.common)

        self.warnings = options.get('warn', False)
        self.calling = []  # todo: remove, use stack
        self.import_stack = []
        self.require_history = {}
        self.result = 0
        self.current_scope = None
        self.ignore_colors = None
        self.property = None
        self.bifs = {}  # todo: implement me!

    def vendors(self):
        return [node.string for node in self.lookup('vendors').nodes]

    def import_file(self, node: Import, file, literal):
        # print(f'importing {file}; {self.import_stack}')

        # handling 'require'
        if node.once:
            if self.require_history[file]:
                return null
            self.require_history[file] = True

            if literal and not self.include_css:
                return node

        # avoid overflows from reimporting the same file
        if file in self.import_stack:
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
        self.import_stack.append(file)
        # todo?: nodes.filename = file

        if literal:
            re.sub('\n\n?', '\n', source)
            literal = Literal(source)
            literal.lineno = 1
            literal.column = 1
            if not self.resolve_url:
                return literal

        # create block
        block: Block = Block(None, None)
        block.lineno = node.lineno
        block.column = node.column
        block.filename = file

        # parse
        merged = {}
        merged.update(self.options)
        merged.update({'root': block})
        parser = Parser(source, merged)

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
                raise ParseError('Issue when parsing an imported file',
                                 filename=file, lineno=line, column=column,
                                 input=source)

        # evaluate imported 'root'
        block = block.clone(self.get_current_block())
        block.parent = self.get_current_block()
        block.scope = False
        ret = self.visit(block)
        self.import_stack.pop()

        if not self.resolve_url or not self.resolve_url:
            self.paths.pop()

        return ret

    def visit(self, node):
        try:
            return super().visit(node)
        except Exception as e:
            if hasattr(e, 'filename'):
                raise e
            input = '[unknown]'
            try:
                with open(node.filename) as f:
                    input = f.read()
            except Exception:
                pass
            raise ParseError(str(self.stack),
                             filename=node.filename,
                             lineno=node.lineno,
                             column=node.column,
                             input=input)

    def setup(self):
        self.populate_global_scope()
        for file in reversed(self.imports):
            expr = Expression()
            expr.append(String(file))
            self.root.nodes.insert(0, Import(expr))

    def populate_global_scope(self):
        """
        Populate the global scope with:
            - css colors
            - user-defined globals
        :return:
        """
        self.common._scope = Scope()

        # colors
        for color, value in colors.items():
            rgba = RGBA(value[0], value[1], value[2], value[3])
            ident = Ident(color, rgba)
            rgba.name = color
            self.common.scope().add(ident)

        # todo: also expose url javascript function; might be hard >8-(
        self.common.scope().add(Ident('embedurl',
                                      Function('embedurl', None, None)))

        # user defined globals
        commons = self.commons
        for common, val in commons.items():
            if val.name:
                self.common.scope().add(Ident(common, val))

    def evaluate(self):
        self.setup()
        return self.visit(self.root)

    def visit_group(self, group: Group):
        # group.nodes = map(self.interpolate, group.nodes)
        new_nodes = []
        for n in group.nodes:
            n.value = self.interpolate(n)
            new_nodes.append(n)
        group.nodes = new_nodes
        group.block = self.visit(group.get_block())
        return group

    def visit_return(self, ret):
        ret.expr = self.visit(ret.expr)
        raise ret

    def visit_media(self, media):
        media.block = self.visit(media.block)
        media.value = self.visit(media.value)
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

    def visit_keyframes(self, keyframes):
        if keyframes.fabricated:
            return keyframes
        keyframes.value = self.interpolate(keyframes).strip()
        val = self.lookup(keyframes.value)
        if val:
            keyframes.val = val.first().string  # || val.first().node_name
        keyframes.block = self.visit(keyframes.block)

        if 'official' != keyframes.prefix:
            return keyframes

        for prefix in self.vendors():
            # IE never had prefixes for keyframes
            if 'ms' == prefix:
                continue
            node = keyframes.clone()
            node.value = keyframes.value
            node.prefix = prefix
            node.block = keyframes.block
            node.fabricated = True
            self.get_current_block().append(node)

        return null

    def visit_function(self, fn, args=None, content=None):
        # check local
        local = self.stack.current_frame().scope().lookup(fn.function_name)
        if local:
            self.warn(f'local {local.node_name} "fn.function_name" '
                      f'previously defined in this scope')

        # user-defined
        user = self.functions.get(fn.function_name, None)
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
        length = len(expr.nodes)
        val = Ident(each.value)
        key = Ident(each.key)
        scope = self.get_current_scope()
        block = self.get_current_block()
        vals = []
        self.result -= 1

        each.get_block().scope = False

        def visit_body(key, value):
            scope.add(value)
            scope.add(key)
            body = self.visit(each.get_block().clone())
            vals.insert(body.nodes)

        # for prop in obj
        if length == 1 and 'object' == expr.nodes[0].name:
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
        if fn and 'expression' == fn.node_name:
            fn = fn.nodes[0]

        # not a function? try user-defined or built-ins
        if fn and 'function' != fn.node_name:
            fn = self.lookup_function(call.function_name)

        # undefined function? render literal css
        if fn is None or fn.node_name != 'function':
            ret = None
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
        if fn and 'expression' == fn.function_name:
            fn = fn.first()

        # evaluate arguments
        self.result += 1
        args = self.visit(call.args)
        for key in args.map:
            args.map[key] = self.visit(args.map[key].clone())
        self.result -= 1

        if hasattr(fn, 'fn') and fn.fn:
            # built-in
            ret = self.invoke_builtin(fn.fn, args)
        elif 'function' == fn.node_name:
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
            prop = self.lookup_property(ident.name)
            if prop:
                return self.visit(prop.expr.clone())
            return null
        elif ident.value.node_name == 'null':
            # lookup
            val = self.lookup(ident.name)
            # object or block mixin
            if val and ident.mixin:
                self.mixin_node(val)
            return self.visit(val) if val else ident
        else:
            # assign
            self.result += 1
            ident.value = self.visit(ident.value)
            self.result -= 1
            self.get_current_scope().add(ident)
            return ident.value

    def visit_binop(self, binop):
        # special case 'is defined' pseudo binop
        if 'is defined' == binop.op:
            return self.is_defined(binop.left)

        self.result += 1
        # visit operands
        op = binop.op
        left = self.visit(binop.left)
        if '||' == op or '&&' == op:
            right = binop.right
        else:
            right = self.visit(binop.right)

        # hack (sic): ternary
        if binop.value:
            value = self.visit(binop.val)
        else:
            value = null

        self.result -= 1

        # operate
        try:
            return self.visit(left.operate(op, right, value))
        except Exception as e:
            # disregard coercion issues in equality
            # checks, and simply return false
            # if 'coercionError' == e:  # fixme: use exception node_name
            #     if op == '==':
            #         return false
            #     elif op == '!=':
            #         return true
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
        for i, node in enumerate(expr.nodes):
            expr.nodes[i] = self.visit(node)

        # support (n * 5)px etc
        if self.castable(expr):
            expr = self.cast(expr)

        return expr

    def visit_arguments(self, args):
        return self.visit_expression(args)

    def visit_property(self, prop):
        name = self.interpolate(prop)
        fn = self.lookup(name)
        call = fn and 'function' == fn.first().node_name
        literal = name in self.calling
        _prop = self.property

        if call and not literal and not prop.literal:
            # function of the same node_name
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
            # fixme: add constructors
            # stylus: block.constructor = nodes.Block;
            return self.visit(Block())

        for i, node in enumerate(list(block.nodes)):
            block.index = i
            block.nodes[i] = self.visit(node)

        return block

    def visit_block(self, block):
        self.stack.append(Frame(block))
        for i, node in enumerate(block.nodes):
            try:
                block.nodes[i] = self.visit(node)
            except Exception as e:
                # fixme: could get a 'return' value type and take action?
                raise e
        self.stack.pop()
        return block

    def visit_atblock(self, atblock):
        atblock.block = self.visit(atblock.block)
        return atblock

    def visit_atrule(self, atrule):
        atrule.value = self.interpolate(atrule)
        if atrule.block:
            atrule.block = self.visit(atrule.block)
        return atrule

    def visit_supports(self, node):
        pass

    def visit_if(self, node):
        pass

    def visit_extend(self, extend):
        pass

    def invoke(self, body, staxk, filename):
        pass

    def mixin(self, nodes, block):
        pass

    def _mixin(self, items, dest, block):
        pass

    def mixin_node(self, node):
        pass

    def mixin_object(self, object):
        pass

    def eval(self, vals):
        pass

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

    def visit_import(self, imported):
        self.result += 1

        path = self.visit(imported.path).first()

        node_name = 'required' if imported.once else 'import'

        self.result -= 1

        # print(f'import {path}')

        # todo: implement me!
        # url() passed
        # if path.name == 'url':
        #     if imported.once:
        #         raise TypeError('You cannot @require a url')
        #     return imported

        # ensure string
        # if not path.string:
        #     raise TypeError(f'@{node_name} string expected')

        name = path = path.string

        # todo: absolute URL or hash

        # todo: literal
        literal = False

        # support optional .styl
        if not literal and not path.endswith('.styl'):
            path += '.styl'

        # lookup
        found = utils.find(path, self.paths, self.filename)
        if not found:
            found = utils.lookup_index(name, self.paths, self.filename)

        # throw if import failed
        if not found:
            raise TypeError(f'failed to locate @{node_name} file {path}')

        block = Block(imported, imported)
        for f in found:
            block.append(self.import_file(imported, f, literal))

        return block

    def lookup_property(self, name):
        pass

    def closest_block(self):
        pass

    def closest_group(self):
        pass

    def selector_stack(self):
        pass

    def property_expression(self, procp, name):
        pass

    def lookup(self, name):
        """
        Lookup `name`, with support for JavaScript functions, and BIFs.
        :param name:
        :return:
        """
        # fixme: this is handled differently on stylus!
        if self.ignore_colors and name in colors:
            return
        val = self.stack.lookup(name)
        if val:
            return utils.unwrap(val)
        else:
            return self.lookup_function(name)

    def interpolate(self, node):
        is_selector = 'selector' == node.node_name

        def to_string(node):
            if node.node_name in ['function', 'ident']:
                return node.name
            elif node.node_name in ['literal', 'string']:
                # huh?
                if self.prefix and not node.prefixed and not node.value.name:
                    node.val = re.sub(r'\.', f'.{self.prefix}', node.val)
                    node.prefixed = True
                return node.value
            elif node.node_name == 'unit':
                # interpolation inside keyframes
                return f'{node.value}%' if '%' == node.type else node.value
            elif node.node_name == 'member':
                return to_string(self.visit(node))
            elif node.node_name == 'expression':
                # prevent cyclic 'selector()' calls
                if self.calling and 'selector' in self.calling and \
                        self._selector:
                    return self.selector
                self.result += 1
                ret = to_string(self.visit(node).first())
                if is_selector:
                    self._selector = ret
                return ret

        if node.segments:
            s = ''
            for segment in node.segments:
                s += str(to_string(segment))
            return s
            # return ''.join(map(to_string, node.segments))
        else:
            return to_string(node)

    def lookup_function(self, name):
        fn = self.functions.get(name, self.bifs.get(name, None))
        if fn:
            return Function(name, fn)

    def is_defined(self, node):
        if 'ident' == node.node_name:
            return Boolean(self.lookup(node.value))  # checkme: or string?
        else:
            raise ParseError(f'invalid "is defined" '
                             f'check on non-variable {node}')

    def cast(self, expr: Expression):
        return Unit(expr.first().value, expr.nodes[1].name)

    def castable(self, expr: Expression):
        return len(expr.nodes) == 2 and \
               expr.first().node_name == 'unit' and \
               expr.nodes[1] and \
               expr.nodes[1].name in units

    def warn(self, message):
        if not self.warnings:
            return
        msg = f'Warning: {message}'
        print(msg)
        log.info(msg)

    def get_current_scope(self):
        return self.stack.current_frame().scope()

    def get_current_frame(self):
        return self.stack.current_frame()

    def get_current_block(self):
        current_frame = self.get_current_frame()
        if current_frame:
            b = current_frame.block
            return b
        return None

    def unvendorize(self, prop: str):
        for vendor in self.vendors():
            if vendor != 'official':
                vendor = f'-{vendor}-'
            if prop in vendor:
                return prop.replace(vendor, '')
        return prop

    def literal_call(self, call):
        call.args = self.visit(call.args)
        return call
