from collections import deque

from stilus.lexer import Lexer, Token
from stilus.nodes.atblock import Atblock
from stilus.nodes.binop import BinOp
from stilus.nodes.block import Block
from stilus.nodes.boolean import true
from stilus.nodes.call import Call
from stilus.nodes.each import Each
from stilus.nodes.expression import Expression
from stilus.nodes.feature import Feature
from stilus.nodes.function import Function
from stilus.nodes.group import Group
from stilus.nodes.ident import Ident
from stilus.nodes.ifnode import If
from stilus.nodes.literal import Literal
from stilus.nodes.media import Media
from stilus.nodes.member import Member
from stilus.nodes.node import Node
from stilus.nodes.property import Property
from stilus.nodes.query_list import QueryList
from stilus.nodes.root import Root
from stilus.nodes.selector import Selector
from stilus.nodes.ternary import Ternary
from stilus.nodes.unaryop import UnaryOp
from stilus.units import units


class ParseError(Exception):

    def __init__(self, message, filename=None, lineno=None,
                 column=None, input=None):
        super().__init__(message)
        self.message = message
        self.filename = filename
        self.lineno = lineno
        self.column = column
        self.input = input


class Parser:

    def __init__(self, s, options: dict):
        self.cond = None
        self.s = s
        self.options = options
        self.lexer = Lexer(s, options)
        self.prefix = options.setdefault('prefix', '')
        self.root = options.setdefault('root', Root())
        self.state = ['root']
        self.stash = []
        self.parens = 0
        self.css = 0
        self.parent = None
        self.selector_scope = None
        self.bracketed = None
        self.in_property = None
        self._ident = None
        self.operand = None

    #
    # Selector composite tokens.
    #
    selector_tokens = [
        'ident',
        'string',
        'stmt_selector',
        'function',
        'comment',
        'boolean',
        'space',
        'color',
        'unit',
        'for',
        'in',
        '[',
        ']',
        '(',
        ')',
        '+',
        '-',
        '*',
        '*=',
        '<',
        '>',
        '=',
        ':',
        '&',
        '&&',
        '~',
        '{',
        '}',
        '.',
        '..',
        '/']

    #
    # CSS pseudo-classes and pseudo-elements.
    # See http://dev.w3.org/csswg/selectors4/
    #
    pseudo_selectors = [
        # Logical Combinations
        'matches',
        'not',

        # Linguistic Pseudo-classes
        'dir',
        'lang',

        # Location Pseudo-classes
        'any-link',
        'link',
        'visited',
        'local-link',
        'target',
        'scope',

        # User Action Pseudo-classes
        'hover',
        'active',
        'focus',
        'drop',

        # Time-dimensional Pseudo-classes
        'current',
        'past',
        'future',

        # The Input Pseudo-classes
        'enabled',
        'disabled',
        'read-only',
        'read-write',
        'placeholder-shown',
        'checked',
        'indeterminate',
        'valid',
        'invalid',
        'in-range',
        'out-of-range',
        'required',
        'optional',
        'user-error',

        # Tree-Structural pseudo-classes
        'root',
        'empty',
        'blank',
        'nth-child',
        'nth-last-child',
        'first-child',
        'last-child',
        'only-child',
        'nth-of-type',
        'nth-last-of-type',
        'first-of-type',
        'last-of-type',
        'only-of-type',
        'nth-match',
        'nth-last-match',

        # Grid-Structural Selectors
        'nth-column',
        'nth-last-column',

        # Pseudo-elements
        'first-line',
        'first-letter',
        'before',
        'after',

        # Non-standard
        'selection']

    def current_state(self):
        return self.state[-1]

    def previous_state(self):
        return self.state[-2]

    def parse(self) -> Node:
        block = self.parent = self.root
        while 'eos' != self.peek().type:
            self.skip_whitespace()
            if 'eos' == self.peek().type:
                break
            stmt = self.statement()
            self.accept(';')
            if not stmt:
                self.error('unexpected token {peek}, not '
                           'allowed at the root level')
            block.append(stmt)
        return block

    def error(self, message: str):
        t = self.peek().type
        value = ''
        if self.peek().value:
            value = str(self.peek())
        if value.strip() == t.strip():
            value = ''
        raise ParseError(message.format(peek='"{}{}"'.format(t, value)))

    def accept(self, types):
        if self.peek().type in types:
            return self.next()
        return None

    def expect(self, type):
        if type != self.peek().type:
            self.error(f'expected "{type}", got {{peek}}')
        return self.next()

    def next(self) -> Token:
        # FIXME: add noline and column and co
        tok = self.lexer.next()
        return tok

    def peek(self) -> Token:
        return self.lexer.peek()

    def lookahead(self, n):
        return self.lexer.lookahead(n)

    def is_selector_token(self, n: int) -> bool:
        """
        Check if the token at n is a valid stmt_selector token.
        :param n:
        :return:
        """
        la = self.lookahead(n).type
        if la == 'for':
            return self.bracketed
        elif la == '[':
            self.bracketed = True
            return True
        elif la == ']':
            self.bracketed = False
            return True
        else:
            return la in self.selector_tokens

    def is_pseudo_selector(self, n):
        value = self.lookahead(n).value
        if value:
            return value.name in self.pseudo_selectors

    def line_contains(self, type):
        i = 1
        la = self.lookahead(i)
        while True:
            if la.type in ['indent', 'outdent', 'newline', 'eos']:
                return False
            if la.type == type:
                return True
            i += 1
            la = self.lookahead(i)

    def selector_token(self):
        """Valid stmt_selector tokens"""
        if self.is_selector_token(1):
            if '{' == self.peek().type:

                if not self.line_contains('}'):
                    # unclosed - must be a block
                    return None

                # check if ':' is within the braces.
                # though not required by Stylus, chances
                # are if someone is using {} they will
                # use CSS-style props, helping us with
                # the ambiguity in this case
                i = 1
                la = self.lookahead(i)
                while la:
                    if la.type == '}':
                        # check empty block
                        if i == 2 or (i == 3 and
                                      self.lookahead(i - 1).type == 'space'):
                            return None
                        break
                    if la.type == ':':
                        return None
                    i += 1
                    la = self.lookahead(i)

            return self.next()
        return None

    def skip(self, tokens):
        while self.peek().type in tokens:
            self.next()

    def skip_whitespace(self):
        self.skip(['space', 'indent', 'outdent', 'newline'])

    def skip_spaces(self):
        self.skip(['space'])

    def skip_spaces_and_comments(self):
        self.skip(['space', 'comment'])

    def looks_like_function_definition(self, i):
        return self.lookahead(i).type in ['indent', '}']

    def looks_like_selector(self, from_property=False):
        i = 1

        # real property
        if from_property and ':' == self.lookahead(i + 1).type and \
                (self.lookahead(i + 1).space or
                 'indent' == self.lookahead(i + 2).type):
            return False

        # assume stmt_selector when an ident is followed by a stmt_selector
        while 'ident' == self.lookahead(i).type and \
                ('newline' == self.lookahead(i + 1).type or
                 ',' == self.lookahead(i + 1).type):
            i += 2

        while self.is_selector_token(i) or ',' == self.lookahead(i).type:

            if 'stmt_selector' == self.lookahead(i).type:
                return True

            if '&' == self.lookahead(i + 1).type:
                return True

            if '.' == self.lookahead(i).type and \
                    'ident' == self.lookahead(i + 1).type:
                return True

            if '*' == self.lookahead(i).type and \
                    'newline' == self.lookahead(i + 1).type:
                return True

            # pseudo-elements
            if ':' == self.lookahead(i).type and \
                    ':' == self.lookahead(i + 1).type:
                return true

            # #a after an ident and newline
            if 'color' == self.lookahead(i).type and \
                    'newline' == self.lookahead(i + 1).type:
                return true

            if self.looks_like_attribute_selector(i):
                return True

            if ('=' == self.lookahead(i).type or 'function' == self.lookahead(
                    i).type) and \
                    '{' == self.lookahead(i + 1).type:
                return False

            # hash values inside properties
            if ':' == self.lookahead(i).type and \
                    not self.is_pseudo_selector(i + 1) and \
                    self.line_contains('.'):
                return False

            # the ':' token within braces signifies
            # a stmt_selector. ex: "foo{bar:'baz'}"
            brace = None
            if '{' == self.lookahead(i).type:
                brace = True
            elif '}' == self.lookahead(i).type:
                brace = False
            if brace and ':' == self.lookahead(i).type:
                return True

            # '{' preceded by a space is considered a stmt_selector.
            # for example "foo{bar}{baz}" may be a property,
            # however "foo{bar} {baz}" is a stmt_selector
            if 'space' == self.lookahead(i).type and \
                    '{' == self.lookahead(i + 1).type:
                return True

            # assume pseudo selectors are NOT properties
            # as 'td:th-child(1)' may look like a property
            # and function call to the parser otherwise
            i += 1
            if ':' == self.lookahead(i).type and \
                    not self.lookahead(i - 1).space and \
                    self.is_pseudo_selector(i):
                return True

            # trailing space
            if 'space' == self.lookahead(i).type and \
                    'newline' == self.lookahead(i + 1).type and \
                    '{' == self.lookahead(i + 2).type:
                return True

            if '.' == self.lookahead(i).type and \
                    'newline' == self.lookahead(i + 1).type:
                return True

        # trailing comma
        if ',' == self.lookahead(i).type and \
                'newline' == self.lookahead(i + 1).type:
            return True

        # trailing brace
        if '{' == self.lookahead(i).type and \
                'newline' == self.lookahead(i + 1).type:
            return True

        # css-style mode, false on ; }
        if self.css and ';' == self.lookahead(i).type and \
                '}' == self.lookahead(i - 1).type:
            return False

        # trailing separators
        while self.lookahead(i).type in ['indent', 'outdent', 'newline', 'for',
                                         'if', ';', '}', 'eos']:
            i += 1

        if 'indent' == self.lookahead(i).type:
            return True

        return False

    def looks_like_attribute_selector(self, n):
        type = self.lookahead(n).type
        if '=' == type and self.bracketed:
            return True
        return ('ident' == type or 'string' == type) and \
            ']' == self.lookahead(n + 1).type and \
            ('newline' == self.lookahead(n + 2).type or
             self.is_selector_token(n + 2)) and \
            not self.line_contains(':') and \
            not self.line_contains('=')

    def looks_like_keyframe(self):
        i = 2
        if self.lookahead(i).type in ['{', 'indent', ',']:
            return True
        elif self.lookahead(i).type == 'newline':
            # FIXME: bad code
            is_unit = 'unit' == self.lookahead(i).type
            is_newline = 'newline' == self.lookahead(i).type
            while is_unit or is_newline:
                i += 1
                type = self.lookahead(i).type
                return 'ident' == type or '{' == type

    def state_allows_selector(self):
        if self.current_state() in ['root', 'atblock', 'stmt_selector',
                                    'conditional', 'function', 'atrule',
                                    'for']:
            return True

    def assign_atblock(self, expr):
        try:
            expr.push(self.atblock(expr))
        except Exception:
            self.error(
                'invalid right-hand side operand in assignment, got {peek}')

    def statement(self):
        stmt = self.stmt()
        state = self.previous_state
        if state in ['assignment', 'expression', 'function arguments']:
            op = self.accept('if')
            if not op:
                op = self.accept('unless')
            if not op:
                op = self.accept('for')

            if op.type in ['if', 'unless']:
                stmt = If(self.expression(), stmt)
                stmt.postfix = true
                stmt.negate = 'unless' == op.type
                self.accept(';')
            elif op.type == 'for':
                val = self.id().name
                if self.accept(','):
                    key = self.id().name
                self.expect('in')
                each = Each(val, key, self.expression())
                block = Block(self.parent, each)
                block.push(stmt)
                each.block = block
                stmt = each
        return stmt

    def stmt(self):
        type = self.peek().type
        if type == 'keyframes':
            return self.keyframes()
        elif type == '-moz-document':
            return self.mozdocument()
        elif type in ['comment', 'stmt_selector', 'literal', 'charset',
                      'namespace', 'import', 'require', 'extend',
                      'media', 'atrule', 'ident', 'scope', 'supports',
                      'unless', 'function', 'for', 'if']:
            return self.__getattribute__(f'stmt_{type}')()
        elif type in 'return':
            return self.resturn()
        elif type == '{':
            return self.property()
        else:
            if self.state_allows_selector():
                if type in ['color', '~', '>', '<', ':',
                            '&', '&&', '[', '.', '/']:
                    return self.stmt_selector()
                elif type == '..':
                    # relative reference
                    if '/' == self.lookahead(2).type:
                        return self.stmt_selector()
                elif type == '+':
                    if 'function' == self.lookahead(2).type:
                        return self.stmt_function()
                    else:
                        return self.stmt_selector()
                elif type == '*':
                    return self.property()
                elif type == 'unit':
                    if self.looks_like_keyframe():
                        return self.stmt_selector()
                elif type == '-':
                    if '{' == self.lookahead(2).type:
                        return self.property()

        expr = self.expression()
        if expr.is_empty():
            self.error('unexpected {peek}')
        return expr

    def stmt_comment(self):
        node = self.next().value
        self.skip_spaces()
        return node

    # todo: implement me!
    def stmt_literal(self):
        pass

    # todo: implement me!
    def stmt_charset(self):
        pass

    # todo: implement me!
    def stmt_namespace(self):
        pass

    # todo: implement me!
    def stmt_import(self):
        pass

    # todo: implement me!
    def stmt_require(self):
        pass

    # todo: implement me!
    def stmt_extend(self):
        pass

    def stmt_media(self):
        self.expect('media')
        self.state.append('atrule')
        media = Media(self.queries())
        media.block(self.block(media))
        self.state.pop()

    def queries(self):
        queries = QueryList()
        while True:
            self.skip(['comment', 'newline', 'space'])
            queries.append(self.query())
            self.skip(['comment', 'newline', 'space'])
            if not self.accept(','):
                break
        return queries

    # todo: implement me!
    def query(self):
        pass

    def feature(self):
        self.skip_spaces_and_comments()
        self.expect('(')
        self.skip_spaces_and_comments()
        node = Feature(self.interpolate())
        self.skip_spaces_and_comments()
        self.accept(':')
        self.skip_spaces_and_comments()
        self.in_property = True
        node.expr = self.list()
        self.in_property = False
        self.skip_spaces_and_comments()
        self.expect(')')
        self.skip_spaces_and_comments()
        return node

    # todo: implement me!
    def stmt_atrule(self):
        pass

    # todo: implement me!
    def stmt_scope(self):
        pass

    # todo: implement me!
    def stmt_supports(self):
        pass

    # todo: implement me!
    def stmt_unless(self):
        pass

    # todo: implement me!
    def stmt_for(self):
        pass

    # todo: implement me!
    def stmt_if(self):
        pass

    def block(self, node, scope=None):
        block = self.parent = Block(self.parent, node)

        if scope is False:
            block.scope = False

        self.accept('newline')

        # css style
        if self.accept('{'):
            self.css += 1
            delim = '}'
            self.skip_whitespace()
        else:
            delim = 'outdent'
            self.expect('indent')

        while delim != self.peek().type:
            # css-style
            if self.css:
                if self.accept('newline') or self.accept('indent'):
                    continue
                stmt = self.statement()
                self.accept(';')
                self.skip_whitespace()
            else:
                if self.accept('newline'):
                    continue
                # skip useless indents and comments
                next = self.lookahead(2).type
                if 'indent' == self.peek().type and \
                        next in ['outdent', 'newline', 'comment']:
                    self.skip(['indent', 'outdent'])
                if 'eos' == self.peek().type:
                    return block
                stmt = self.statement()
                self.accept(';')
            if not stmt:
                self.error('unexpected token {peek} in block')
            block.append(stmt)

        # css-style
        if self.css:
            self.skip_whitespace()
            self.expect('}')
            self.skip_spaces()
            self.css -= 1
        else:
            self.expect('outdent')

        self.parent = block.parent
        return block

    def stmt_selector(self):
        scope = self.selector_scope
        group = Group()
        is_root = self.current_state() == 'root'

        while True:
            self.accept('newline')  # clobber newline after ','
            arr = self.selector_parts()

            # push the stmt_selector
            if is_root and scope:
                arr.appendleft(Literal(f'{scope} '))
            if len(arr) > 0:
                selector = Selector(arr)
                selector.lineno = arr[0].lineno
                selector.column = arr[0].column
                group.push(selector)

            # CHECK ME: True or False; huh?
            if (self.accept(',') or self.accept('newline')) is None:
                break

        if 'stmt_selector-parts' == self.current_state():
            return group.nodes

        self.state.append('stmt_selector')
        group.set_block(self.block(group))
        self.state.pop()

        return group

    def selector_parts(self) -> deque:
        """Selector candidates, stitched together to form a stmt_selector."""
        arr = deque()
        while True:
            tok = self.selector_token()
            if tok:
                if tok.type == '{':
                    self.skip_spaces()
                    expr = self.expression()
                    self.skip_spaces()
                    self.expect(';')
                    arr.append(expr)
                elif tok.type == self.prefix and '.':
                    literal = Literal(tok.value + self.prefix)
                    literal.prefixed = True
                    arr.append(literal)
                elif tok.type == 'comment':
                    # ignore comments
                    pass
                elif tok.type in ['color', 'unit']:
                    arr.append(Literal(tok.value.raw))
                elif tok.type == 'space':
                    arr.append(Literal(' '))
                elif tok.type == 'function':
                    arr.append(Literal(f'{tok.value.node_name}('))
                elif tok.type == 'ident':
                    # FIXME: string vs node_name?
                    arr.append(Literal(tok.value.string))
                else:
                    arr.append(Literal(tok.value))
                    if tok.space:
                        arr.append(Literal(' '))
            else:
                break
        return arr

    def assignment(self):
        name = self.id().name
        op = self.accept(['=', '?=', '+=', '-=', '*=', '/=', '%='])
        if op:
            self.state.append('assignment')
            expr = self.list()
            # @block support
            if expr.is_empty():
                self.assign_atblock(expr)
            node = Ident(name, expr)
            self.state.pop()

            if op.type == '?=':
                defined = BinOp('is defined', node)
                lookup = Expression()
                lookup.append(Ident(name))
                node = Ternary(defined, lookup, node)
            elif op in ['+=', '-=', '*=', '/=', '%=']:
                node.value = BinOp(op.type[0], Ident(name), expr)

        return node

    def stmt_ident(self):
        i = 2
        la = self.lookahead(i).type

        while 'space' == la:
            i += 1
            la = self.lookahead(i).type

        if la in ['=', '?=', '-=', '+=', '*=', '/=', '%=']:
            # assignment
            return self.assignment()
        elif la == '.':
            # member
            if 'space' == self.lookahead(i - 1).type:
                return self.stmt_selector()
            if self._ident == self.peek():
                return self.id()
            i += 1
            while '=' != self.lookahead(i).type and self.lookahead(i) in \
                    ['[', ',', 'newline', 'indent', 'eos']:
                pass
            if '=' != self.lookahead(i).type:
                self._ident = self.peek()
                return self.expression()
            elif self.looks_like_attribute_selector() and \
                    self.state_allows_selector():
                return self.stmt_selector()
            else:
                # huh?
                pass
        elif la == '[':
            # assignment []=
            if self._indent == self.peek():
                return self._id()
            while ']' != self.lookahead(i).type and \
                    'stmt_selector' != self.lookahead(i) and \
                    'oes' != self.lookahead(i):
                i += 1
            if '=' == self.lookahead(i).type:
                self._indent = self.peek()
                return self.expression()
            elif self.looks_like_selector() and self.state_allows_selector():
                return self.stmt_selector()
        elif la in ['-', '+', '/', '*', '%', '**', '&&', '||', '>', '<', '>=',
                    '<=', '!=', '==', '?', 'in', 'is a', 'is defined']:
            # operation
            # prevent cyclic .ident, return literal
            if self._ident == self.peek():
                return self.id()
            else:
                self._ident = self.peek()
                if self.current_state() in ['for', 'stmt_selector']:
                    return self.property()
                elif self.current_state() in ['root', 'atblock', 'atrule']:
                    if '[' == la:
                        return self.subscript()
                    else:
                        return self.stmt_selector()
                elif self.current_state() in ['function', 'conditional']:
                    if self.looks_like_selector():
                        return self.stmt_selector()
                    else:
                        return self.expression()
                else:
                    # do not disrupt the ident when an operand
                    if self.operand:
                        self.id()
                    else:
                        self.expression()
        else:
            if self.current_state() == 'root':
                return self.stmt_selector()
            elif self.current_state() in ['for', 'stmt_selector', 'function',
                                          'conditional', 'atblock', 'atrule']:
                return self.property()
            else:
                id = self.id()
                if 'interpolation' == self.previous_state():
                    id.mixin = True
                return id

    def property(self):
        if self.looks_like_selector(True):
            return self.stmt_selector()

        # property
        ident = self.interpolate()
        prop = Property(ident)
        ret = prop

        # optional ':'
        self.accept('space')
        if self.accept(':'):
            self.accept('space')

        self.state.append('property')
        self.in_property = True
        prop.expr = self.list()
        if len(prop.expr) == 0:
            ret = ident[0]
        self.in_property = False
        self.allow_postfix = True
        self.state.pop()

        # optional ';'
        self.accept(';')

        return ret

    def interpolate(self):
        node = None
        segs = []

        star = self.accept('*')
        if star:
            segs.append(Literal('*'))

        while True:
            peek = self.peek()
            if peek.type == '{':
                self.next()
                self.state.append('interpolation')
                segs.append(self.expression())
                self.expect('}')
            elif peek.type == '-':
                self.next()
                segs.append(Literal('-'))
            elif peek.type == 'ident':
                node = self.next()
                segs.append(node.value)
            else:
                break

        # empty segment list
        if len(segs) == 0:
            self.expect('ident')

        return segs

    def expression(self):
        """negation+"""
        expr = Expression()
        self.state.append('expression')
        while True:

            node = self.negation()
            if not node:
                break
                # fixme
                self.error('unexpected token {peek} in expression')
            expr.append(node)
        self.state.pop()
        return expr

    def negation(self):
        if self.accept('not'):
            return UnaryOp('!', self.negation())
        return self.ternary()

    def ternary(self):
        node = self.logical()
        if self.accept('?'):
            true_expr = self.expression()
            self.expect(':')
            false_expr = self.expression()
            node = Ternary(node, true_expr, false_expr)
        return node

    def list(self):
        """expression (',' expression)*"""
        node = self.expression()

        while self.accept(','):
            if node.is_list:
                list.append(self.expression())
            else:
                list = Expression(true)
                list.push(node)
                list.push(self.expression())
                node = list

        return node

    def logical(self):
        node = self.typecheck()
        while True:
            op = self.accept(['&&', '||'])
            if op:
                node = BinOp(op.type, node, self.typecheck())
            else:
                break
        return node

    def typecheck(self):
        node = self.equality()
        while True:
            op = self.accept('is a')
            if op:
                self.operand = True
                if not node:
                    self.error(f'illegal unary "{op}", '
                               f'missing left-hand operand')
                node = BinOp(op.type, node, self.equality())
                self.operand = False
            else:
                break
        return node

    def equality(self):
        node = self.inn()
        while True:
            op = self.accept(['==', '!='])
            if op:
                self.operand = True
                if not node:
                    self.error(f'illegal unary "{op}", '
                               f'missing left-hand operand')
                node = BinOp(op.type, node, self.inn())
                self.operand = False
            else:
                break
        return node

    def inn(self):
        node = self.relational()
        while self.accept('in'):
            self.operand = True
            if not node:
                self.error('illegal unary "in", '
                           'missing left-hand operand')
            node = BinOp('in', node, self.relational())
            self.operand = False
        return node

    def relational(self):
        node = self.range()
        op = self.accept(['>=', '<=', '<', '>'])
        if op:
            self.operand = True
            if not node:
                self.error(f'illegal unary "{op}", '
                           f'missing left-hand operand')
            node = BinOp(op.type, self.range())
            self.operand = False
        return node

    def stmt_function(self):
        with_block = self.accept('+')
        if 'url' == self.peek().value.name:
            return self.url()
        name = self.expect('function').value.name
        self.state.append('function arguments')
        self.parens += 1
        args = self.args()
        self.expect(')')
        self.parems -= 1
        self.state.pop()
        call = Call(name, args)
        if with_block:
            self.state.append('function')
            call.block = self.block(call)
            self.state.pop()
        return call

    def range(self):
        node = self.additive()
        op = self.accept(['...', '..'])
        if op:
            self.operand = True
            if not node:
                self.error(f'illegal unary "{op}", missing left-hand operand')
            node = BinOp(op.value, node, self.additive())
            self.operand = False
        return node

    def additive(self):
        node = self.multiplicative()
        op = self.accept(['+', '-'])
        if op:
            self.operand = True
            node = BinOp(op.type, node, self.multiplicative())
            self.operand = False
        return node

    def multiplicative(self):
        node = self.defined()
        op = self.accept(['**', '*', '/', '%'])
        if op:
            self.operand = True
            if '/' == op and self.in_property and len(self.parens) < 0:
                self.stash.append(Token('literal', Literal('/')))
                self.operand = False
                return node
            else:
                if not node:
                    self.error(f'illegal unary "{op}", '
                               f'missing left-hand operand')
                    node = BinOp(op.type, node, self.defined())
                    self.operand = False
        return node

    def defined(self):
        node = self.unary()
        if self.accept('is defined'):
            if not node:
                self.error(f'illegal unary "is defined", '
                           f'missing left-hand operand')
            node = BinOp('is defined', node)
        return node

    def unary(self):
        op = self.accept(['!', '~', '+', '-'])
        if op:
            self.operand = True
            node = self.unary()
            if not node:
                self.error(f'illegal unary "{op}"')
            node = UnaryOp(op.type, node)
            self.operand = False
            return node
        return self.subscript()

    def subscript(self):
        node = self.member()
        while self.accept('['):
            node = BinOp('[]', node, self.expression())
            self.expect(']')
        if self.accept('='):
            node.op += '='
            node.value = self.list()
            # @block suppprt
            if node.value.is_empty():
                self.assign_atblock(node.value)
        return node

    def member(self):
        node = self.primary()
        if node:
            while self.accept('.'):
                id = Ident(self.expect('ident').value.string)
                node = Member(node, id)
            self.skip_spaces()
            if self.accept('='):
                node.value = self.list()
                # @block support
                if node.value.is_empty():
                    self.assign_atblock(node.value)
        return node

    def primary(self):
        self.skip_spaces()

        # parenthesis
        if self.accept('('):
            self.parens += 1
            expr = self.expression()
            paren = self.expect(')')
            self.parens -= 1
            if self.accept('%'):
                expr.push(Ident('%'))
            tok = self.peek()
            # (1 + 2)px, (1 + 2)em, etc.
            if not paren.space and 'ident' == tok.type and \
                    tok.value.string not in units:
                self.next()
            return expr

        tok = self.peek()

        # primitive
        if tok.type in ['null', 'unit', 'color', 'string', 'literal',
                        'boolean', 'comment']:
            return self.next().value
        elif not self.cond and tok.type == '{':
            return self.object()
        elif tok.type == 'atblock':
            return self.atblock()
        # property lookup
        elif tok.type == 'atrule':
            id = Ident(self.next().value)
            id.property = True
            return id
        elif tok.type == 'ident':
            return self.stmt_ident()
        elif tok.type == 'function':
            if tok.anonymous:
                return self.fuction_definition()
            else:
                return self.stmt_function()

    def fuction_definition(self):
        name = self.expect('function').value.name

        # params
        self.state.append('function param')
        self.skip_whitespace()
        params = self.params()
        self.skip_whitespace()
        self.expect(')')
        self.state.pop()

        # body
        self.state.push('function')
        fn = Function(name, params)
        fn.block = self.block(fn)
        self.state.pop()
        return Ident(name, fn)

    def id(self):
        tok = self.expect('ident')
        self.accept('space')
        return tok.value

    def atblock(self, node):
        if not node:
            self.expect('atblock')
        node = Atblock()
        self.state.append('atblock')
