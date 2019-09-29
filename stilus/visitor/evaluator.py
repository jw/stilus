import inspect
import logging
import os
import re
from pathlib import Path

from stilus import utils
from stilus.colors import colors
from stilus.exceptions import ParseError, StilusError
from stilus.functions.bifs import bifs, raw_bifs
from stilus.nodes.arguments import Arguments
from stilus.nodes.block import Block
from stilus.nodes.boolean import Boolean, false
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
from stilus.nodes.return_node import ReturnNode
from stilus.nodes.string import String
from stilus.nodes.unit import Unit
from stilus.parser import Parser
from stilus.stack.frame import Frame
from stilus.stack.scope import Scope
from stilus.stack.stack import Stack
from stilus.units import units
from stilus.utils import unwrap
from stilus.visitor.visitor import Visitor

log = logging.getLogger(__name__)


class Evaluator(Visitor):

    def __init__(self, root, parser, options: dict):
        super().__init__(root)
        self.parser = parser
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
        self.bifs = bifs

    def vendors(self):
        return [node.string for node in self.lookup('vendors').nodes]

    def import_file(self, node: Import, file, literal, lineno=1, column=1):
        log.debug(f'importing {file}; {self.import_stack}')

        # handling 'require'
        if node.once:
            if self.require_history.get(file, False):
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
        node.dirname = Path(file).parent
        # store modified time
        node.mtime = os.stat(file).st_mtime
        self.paths.append(str(node.dirname))

        if '_imports' in self.options:
            self.options['_imports'].append(node.clone())

        # parse the file
        self.import_stack.append(file)
        # todo?: nodes.filename = file

        if literal:
            re.sub('\n\n?', '\n', source)
            literal = Literal(source, lineno=self.parser.lineno,
                              column=self.parser.column)
            literal.lineno = 1
            literal.column = 1
            if not self.resolve_url:
                return literal

        # create block
        block = Block(None, None, lineno=lineno, column=column)
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
        except StilusError as se:
            if not se.filename:
                raise se
            try:
                with open(str(se.filename)) as f:
                    input = f.read()
            except (AttributeError, FileNotFoundError):
                pass
            raise StilusError(self.stack,
                              filename=node.filename,
                              lineno=node.lineno,
                              column=node.column,
                              input=input)

    def setup(self):
        self.populate_global_scope()
        for file in reversed(self.imports):
            expr = Expression()
            expr.append(String(file, lineno=self.parser.lineno,
                               column=self.parser.column))
            self.root.nodes.insert(0, Import(expr,
                                             lineno=self.parser.lineno,
                                             column=self.parser.column))

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
                                      Function('embedurl', None, None,
                                               lineno=self.parser.lineno,
                                               column=self.parser.column)))

        # user defined globals
        commons = self.commons
        for common, val in commons.items():
            if val.name:
                self.common.scope().add(Ident(common, val))

    def evaluate(self):
        self.setup()
        return self.visit(self.root)

    def visit_group(self, group: Group):
        new_nodes = []
        for selector in group.nodes:
            selector.value = self.interpolate(selector)
            new_nodes.append(selector)
        group.nodes = new_nodes
        group.block = self.visit(group.block)
        return group

    def visit_returnnode(self, ret):
        ret.expression = self.visit(ret.expression)
        raise ret

    def visit_media(self, media):
        media.block = self.visit(media.block)
        media.value = self.visit(media.value)
        return media

    def visit_querylist(self, queries):
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

    def visit_objectnode(self, obj: ObjectNode):
        for key in obj.values.keys():
            pass
            # print(f'key: {key}; value: {obj.values[key]}')
            # obj.values[key] = self.visit(obj.values[key])
        return obj

    def visit_member(self, node):
        left = node.left
        right = node.right
        obj = self.visit(left).first()

        if 'objectnode' != obj.node_name:
            raise ParseError(f'{left} has no property .{right}')

        if node.value:
            self.result += 1
            obj.set(right.value, self.visit(node.value))
            self.result -= 1

        return obj.values.get(right.name)

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

        if fn.function_name in bifs:
            self.warn(f'built-in function "{fn.function_name}" '
                      f'is already defined [NOT IMPLEMENTED YET!]')

        return fn

    def visit_each(self, each):
        self.result += 1
        expr = utils.unwrap(self.visit(each.expr))
        length = len(expr.nodes)
        val = Ident(each.value)
        key = Ident('__index__')
        if each.key:
            key = Ident(each.key)
        scope = self.get_current_scope()
        block = self.get_current_block()
        vals = []
        self.result -= 1

        each.block.scope = False

        def visit_body(key, value):
            scope.add(value)
            scope.add(key)
            body = self.visit(each.block.clone())
            vals.extend(body.nodes)

        # for prop in obj
        if length == 1 and 'objectnode' == expr.nodes[0].node_name:
            obj = expr.nodes[0]
            for prop in obj.values:
                val.value = String(prop, lineno=self.parser.lineno,
                                   column=self.parser.column)
                key.value = obj.get(prop)  # checkme: works?
                visit_body(key, val)
        else:
            for i, n in enumerate(expr.nodes):
                val.value = n
                key.value = Unit(i)
                visit_body(key, val)

        self.mixin(vals, block)

        if vals and len(vals) > 0:
            return vals[len(vals) - 1]
        else:
            return null

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
                    ret = Literal(call.function_name + call.args.nodes[0],
                                  lineno=self.parser.lineno,
                                  column=self.parser.column)
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

        if fn.builtin:
            # built-in
            ret = self.invoke_builtin(fn.params, args)
        elif 'function' == fn.node_name:
            # user-defined
            # evaluate mixin block
            if call.block:
                call.block = self.visit(call.block)
            ret = self.invoke_function(fn, args, call.block)

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
            if val is not None and ident.mixin:
                self.mixin_node(val)
            if val is not None:
                return self.visit(val)
            else:
                return ident
            # return self.visit(val) if val is not None else ident
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
            value = self.visit(binop.value)
        else:
            value = null

        self.result -= 1

        # operate
        try:
            return self.visit(left.operate(op, right, value))
        except Exception as e:
            print(e)
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
            if isinstance(node.value, float):
                node.value = ~int(node.value)
            else:
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
        expr.nodes = [self.visit(node) for node in expr.nodes]

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

        prop_lit = True if hasattr(prop, 'literal') and prop.literal else False
        if call and not literal and not prop_lit:
            # function of the same node_name
            clone = prop.expr.clone(None, None)
            args = Arguments.from_expression(utils.unwrap(clone))
            prop.name = name
            self.property = prop
            self.result += 1
            self.property.expr = self.visit(prop.expr)
            self.result -= 1
            ret = self.visit(Call(name, args, lineno=self.parser.lineno,
                                  column=self.parser.column))
            self.property = _prop
            return ret
        else:
            # regular property
            self.result += 1
            prop.name = name
            prop.literal = True
            self.property = prop
            prop.expr = self.visit(prop.expr)
            self.property = _prop
            self.result -= 1
            return prop

    def visit_root(self, block):
        if block != self.root:
            # normalize cached imports
            # fixme: add constructors
            # stylus: block.constructor = nodes.Block;
            return self.visit(Block())

        # for i, node in enumerate(list(block.nodes)):
        i = 0
        while i < len(block.nodes):
            block.index = i
            v = self.visit(block.nodes[i])
            if hasattr(block, 'mixin') and block.mixin:
                log.debug(f'Not adding mixin [{v}]!')
                block.mixin = False
            else:
                block.nodes[i] = v
            i += 1

        return block

    def visit_block(self, block):
        self.stack.append(Frame(block))

        index = 0
        while index < len(block.nodes):
            block.index = index
            try:
                v = self.visit(block.nodes[block.index])
                if block.mixin:
                    log.debug(f'Not adding mixin [{v}]!')
                    block.mixin = False
                else:
                    try:
                        block.nodes[index] = v
                    except TypeError:
                        pass

            except ReturnNode as rn:
                if self.result:
                    self.stack.pop()
                    raise rn
                else:
                    block.nodes[block.index] = rn
                    break

            index = block.index + 1
            block.index += 1

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
        condition = node.condition
        self.result += 1
        node.condition = self.visit(condition)
        self.result -= 1
        value = condition.first()
        if len(condition.nodes) == 1 and value.node_name == 'string':
            node.condition = value.string
        node.block = self.visit(node.block)
        return node

    def visit_if(self, node):
        block = self.get_current_block()
        negate = node.negate
        self.result += 1
        ok = self.visit(node.cond).first().to_boolean()
        self.result -= 1

        node.block.scope = \
            hasattr(node.block, 'has_media') and \
            node.block.has_media()

        # evaluate body
        ret = None
        if negate:
            # unless
            if ok.is_false():
                ret = self.visit(node.block)
        else:
            # if
            if ok.is_true():
                ret = self.visit(node.block)
            # else
            elif node.elses:
                for b in node.elses:
                    # else if
                    if hasattr(b, 'cond') and b.cond:
                        b.block.scope = b.block.has_media()
                        self.result += 1
                        cond = self.visit(b.cond).first().to_boolean()
                        self.result -= 1
                        if cond.is_true():
                            ret = self.visit(b.block)
                            break
                    # else:
                    else:
                        b.scope = b.has_media()
                        ret = self.visit(b)

        # mixin conditional statements within
        # a selector group or at-rule
        if ret and not node.postfix and block.node and \
                block.node.node_name in ['group', 'atrule', 'media',
                                         'supports', 'keyframes']:
            self.mixin(ret.nodes, block)
            return null

        if ret:
            return ret
        return null

    def visit_extend(self, extend, id=None):
        block = self.get_current_block()
        if block.node.node_name != 'group':
            block = self.closest_group()
        for selector in extend.selectors:
            c = selector.clone()
            # todo: this is really bad; refactor this
            some_object = {'selector': self.interpolate(c).strip(),
                           'optional': selector.optional,
                           'lineno': c.lineno,
                           'column': c.column}
            block.node.extends.append(some_object)
        return null

    def invoke(self, body, stack=None, filename=None):
        if filename:
            self.paths.append(str(Path(filename).parent))

        if self.result:
            ret = self.eval(body.nodes)
            if stack:
                self.stack.pop()
        else:
            body = self.visit(body)  # <---
            if stack:
                self.stack.pop()
            self.mixin(body.nodes, self.get_current_block())
            ret = null

        if filename:
            self.paths.pop()

        return ret

    # todo: rewrite this; this is not Python nor proper code >:-(
    def mixin(self, nodes, block):

        def prettify(nodes):
            buffer = [f' -> {node}' for node in nodes]
            return '\n'.join(buffer)

        # log.debug(f'Mixin: in: nodes:\n{prettify(nodes)}')
        # log.debug(f'Mixin: in: block: {block}')
        # log.debug(f'Mixin: in: block.nodes:\n{prettify(block.nodes)}')
        if len(nodes) == 0:
            return None
        head = block.nodes[:block.index]
        tail = block.nodes[block.index + 1:]
        self._mixin(nodes, head, block)
        block.index = 0
        block.mixin = True
        head.extend(tail)
        block.nodes = head
        # log.debug(f'Mixin: out: {prettify(block.nodes)}')
        # self.set_current_block(block)

    # todo: rewrite this; this is not Python >:-(
    def _mixin(self, items, dest, block):
        for item in items:
            checked = False
            media_passed = False
            if item.node_name == 'return':
                return
            elif item.node_name == 'block':
                checked = True
                self._mixin(item.nodes, dest, block)
            elif item.node_name == 'media':
                # fix link to the parent block
                parent_node = item.block.parent.node
                if parent_node and parent_node.node_name != 'call':
                    item.block.parent = block
                media_passed = True
            if media_passed or item.node_name == 'property':
                value = None
                if hasattr(item, 'expr'):
                    value = item.expr
                # prevent `block` mixin recursion
                if hasattr(item, 'literal') and \
                        item.literal and \
                        hasattr(value, 'first') and \
                        value.first().node_name == 'block':
                    value = unwrap(value)
                    value.nodes[0] = Literal('block',
                                             lineno=self.parser.lineno,
                                             column=self.parser.column)
            if not checked:
                dest.append(item)

    def mixin_node(self, node):
        node = self.visit(node.first())
        if node.node_name == 'objectnode':
            self.mixin_object(node)
            return null
        elif node.node_name in ['block', 'atblock']:
            self.mixin(node.nodes, self.get_current_block())
            return null

    def mixin_object(self, object):
        raise NotImplementedError

    def eval(self, vals=None):
        if vals is None:
            return null

        def update(node):
            do_visit = True
            skip_next = False
            if node.node_name == 'if':
                if node.block.node_name != 'block':
                    node = self.visit(node)
                    do_visit = False
                    skip_next = True
            if not skip_next and node.node_name in ['if', 'each', 'block']:
                node = self.visit(node)
                if hasattr(node, 'nodes') and node.nodes:
                    node = self.eval(node.nodes)
                do_visit = False
            if do_visit:
                node = self.visit(node)
            return node

        try:
            nodes = [update(node) for node in vals]
        except ReturnNode as rn:
            return rn.expression

        return nodes[-1] if nodes else null

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
        # via raw_bifs
        if hasattr(fn, '__name__') and fn.__name__ in raw_bifs:
            ret = args.nodes
        else:
            ret = []
            # fit in the args to the functions
            sig = inspect.signature(fn)
            i = 0
            # remove the last parameter (the evaluator) first
            keys = [key for key in sig.parameters.keys()][:-1]
            for key in keys:
                param = sig.parameters.get(key)
                # handle the *args parameters
                if param.name == 'args':
                    while i < len(args.nodes):
                        ret.append(utils.unwrap(args.nodes[i].first()))
                        i += 1
                # regular parameters
                elif param.name in args.map.keys():
                    # in the map
                    ret.append(args.map[param.name].first())
                elif i < len(args.nodes):
                    # then in the nodes
                    ret.append(utils.unwrap(args.nodes[i].first()))
                    i += 1
                # else: assume remaining parameters are not required

        # invoke builtin function
        body = utils.coerce(fn(*ret, evaluator=self),
                            False,
                            lineno=self.parser.lineno,
                            column=self.parser.column)

        # Always wrapping allows js functions
        # to return several values with a single
        # Expression node
        expr = Expression()
        expr.append(body)
        body = expr

        return self.invoke(body)

    def visit_import(self, imported):
        literal = False
        self.result += 1

        path = self.visit(imported.path).first()

        node_name = 'require' if imported.once else 'import'

        self.result -= 1

        log.debug(f'import {path}')

        # url() passed
        # if path.name == 'url':
        #     if hasattr(imported, 'once') and imported.once:
        #         raise StilusError('You cannot @require a url')
        #     return imported

        # ensure string
        # if not path.string:
        #     raise StilusError(f'@{node_name} string expected')

        name = path = path.string

        # todo: absolute URL or hash

        if path.endswith('.css'):
            literal = True
            if not imported and not self.include_css:
                return imported

        # support optional .styl
        if not literal and not path.endswith('.styl'):
            path += '.styl'

        # lookup
        found = utils.find(path, self.paths, self.filename)
        if not found:
            found = utils.lookup_index(name, self.paths, self.filename)

        # throw if import failed
        if not found:
            raise TypeError(f'failed to locate @{node_name} file in {path}'
                            f' {self.paths}')

        block = Block(None, None, lineno=self.parser.lineno,
                      column=self.parser.column)
        for f in found:
            block.append(self.import_file(imported, f, literal,
                                          lineno=self.parser.lineno,
                                          column=self.parser.column))

        return block

    def lookup_property(self, name):
        raise NotImplementedError

    def closest_block(self):
        for stack in reversed(self.stack):
            block = stack.block
            if hasattr(block, 'node') and block.node and \
                    block.node.node_name in ['group', 'keyframes',
                                             'atrule', 'atblock',
                                             'media', 'call']:
                return block
        # todo: create warning when entering here
        return None

    def closest_group(self):
        for s in self.stack:
            b = s.block
            if hasattr(b, 'node') and b.node and b.node.node_name == 'group':
                return b

    def selector_stack(self):
        stack = []
        for s in self.stack:
            b = s.block
            if hasattr(b, 'node') and b.node and b.node.node_name == 'group':
                for s in b.node.nodes:
                    if not s.value:
                        s.value = self.interpolate(s)
                stack.append(b.node.nodes)
        return stack

    def property_expression(self, prop, name):
        expr = Expression(lineno=self.parser.lineno,
                          column=self.parser.column)
        value = prop.expr.clone(None)

        # name
        expr.append(String(prop.name, lineno=self.parser.lineno,
                           column=self.parser.column))

        # replace cyclic call with __CALL__
        def replace(node):
            if node.node_name == 'call' and hasattr(node, 'function_name') \
                    and name == node.function_name:
                return Literal('__CALL__',
                               lineno=self.parser.lineno,
                               column=self.parser.column)
            if hasattr(node, 'nodes') and node.nodes:
                node.nodes = [replace(n) for n in node.nodes]
            return node

        replace(value)
        expr.append(value)
        return expr

    def lookup(self, name):
        """
        Lookup `name`, with support for JavaScript functions, and BIFs.
        :param name:
        :return:
        """
        if self.ignore_colors and name in colors:
            return
        val = self.stack.lookup(name)
        if val is not None:  # fixme: implement __len__()
            return utils.unwrap(val)
        else:
            return self.lookup_function(name)

    def interpolate(self, node):
        is_selector = 'selector' == node.node_name

        def to_string(node):
            if node.node_name == 'ident':
                return node.name
            elif node.node_name == 'function':
                return node.function_name
            elif node.node_name in ['literal', 'string']:
                if self.prefix and not node.prefixed and \
                        not hasattr(node.value, 'node_name'):
                    node.value = re.sub(r'\.', f'.{self.prefix}', node.value)
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
                    return self._selector
                self.result += 1
                ret = to_string(self.visit(node).first())
                self.result -= 1
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
        function = self.functions.get(name, self.bifs.get(name, None))
        if function:
            return Function(name, function, lineno=self.parser.lineno,
                            column=self.parser.column)
        else:
            return None

    def is_defined(self, node):
        if 'ident' == node.node_name:
            return Boolean(self.lookup(node.name))
        else:
            raise ParseError(f'invalid "is defined" '
                             f'check on non-variable {node}')

    def cast(self, expr: Expression):
        return Unit(expr.first().value, expr.nodes[1].name)

    def castable(self, expr: Expression):
        return len(expr.nodes) == 2 and \
               expr.first().node_name == 'unit' and \
               expr.nodes[1] and \
               expr.nodes[1].node_name in units

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

    def set_current_block(self, block):
        current_frame = self.get_current_frame()
        if current_frame:
            current_frame.block = block
        else:
            raise TypeError

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

    def invoke_function(self, fn, args, content):
        block = Block(fn.block.parent, None, lineno=self.parser.lineno,
                      column=self.parser.column)

        # clone the function body to prevent mutation of subsequent calls
        body = fn.block.clone(block)

        mixin_block = self.stack.current_frame().block

        # new block scope
        self.stack.append(Frame(block))
        scope = self.get_current_scope()

        # normalize arguments
        if args.node_name != 'arguments':
            expr = Expression()
            expr.append(args)
            args = Arguments.from_expression(expr)

        # arguments loca
        scope.add(Ident('arguments', args))

        # mixin scope introspection
        bn = mixin_block.node_name
        if self.result:
            scope.add(Ident('mixin', false))
        else:
            scope.add(Ident('mixin', String(bn,
                                            lineno=self.parser.lineno,
                                            column=self.parser.column)))

        # current property
        if self.property:
            prop = self.property_expression(self.property, fn.function_name)
            scope.add(Ident('current-property', prop,
                            lineno=self.parser.lineno,
                            column=self.parser.column))
        else:
            scope.add(Ident('current-property', null,
                            lineno=self.parser.lineno,
                            column=self.parser.column))

        # current call stack
        expr = Expression(lineno=self.parser.lineno, column=self.parser.column)
        for call in self.calling[:-1]:
            expr.append(Literal(call, lineno=self.parser.lineno,
                                column=self.parser.column))
        scope.add(Ident('called-from', expr,
                        lineno=self.parser.lineno,
                        column=self.parser.column))

        # inject arguments as locals
        i = 0
        for node in fn.params.nodes:
            # rest param support
            if node.rest:
                node.value = Expression(lineno=self.parser.lineno,
                                        column=self.parser.column)
                for n in args.nodes[i:]:
                    node.value.append(n)
                node.value.preserve = True
                node.value.is_list = args.is_list
            else:
                # argument default support

                # in dict?
                arg = args.map.get(node.name)
                # next node?
                if not arg and hasattr(args, 'nodes') and i < len(args.nodes):
                    arg = args.nodes[i]
                    i += 1

                node = node.clone()
                if arg:
                    if hasattr(arg, 'is_empty') and arg.is_empty():
                        args.nodes[i-1] = self.visit(node)  # todo: fixme!
                    else:
                        node.value = arg
                else:
                    args.append(node.value)

                # required argument not satisfied
                if not node.value:
                    raise TypeError(f'argument "{node}" required for {fn}')

            scope.add(node)

        # mixin block
        if content:
            scope.add(Ident('block', content, True))

        # invoke
        return self.invoke(body, True, fn.filename)
