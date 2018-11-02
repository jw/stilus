from collections import deque

from stilus.lexer import Lexer, Token
from stilus.nodes.binop import BinOp
from stilus.nodes.block import Block
from stilus.nodes.boolean import true
from stilus.nodes.each import Each
from stilus.nodes.expression import Expression
from stilus.nodes.group import Group
from stilus.nodes.ifnode import If
from stilus.nodes.literal import Literal
from stilus.nodes.node import Node
from stilus.nodes.property import Property
from stilus.nodes.root import Root
from stilus.nodes.selector import Selector
from stilus.nodes.ternary import Ternary
from stilus.nodes.unaryop import UnaryOp


class ParseError(Exception):
    pass


# FIXME: clean up and test this class
class Parser:

    def __init__(self, s, options: dict):
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

    #
    # Selector composite tokens.
    #
    selector_tokens = [
        'ident',
        'string',
        'selector',
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
            block.push(stmt)
        return block

    def error(self, message: str):
        t = self.peek().type
        value = ''
        if self.peek().value:
            value = str(self.peek())
        if value.strip() == t.strip():
            value = ''
        raise ParseError(message.format(peek='"{}{}"'.format(t, value)))

    def accept(self, type):
        if self.peek().type == type:
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

    def is_selector_token(self, n):
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
        """Valid selector tokens"""
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

        while 'ident' == self.lookahead(i).type and \
                ('newline' == self.lookahead(i + 1).type or
                 ',' == self.lookahead(i + 1).type):
            i += 2

        while self.is_selector_token(i) or ',' == self.lookahead(i).type:

            if 'selector' == self.lookahead(i).type:
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
            # a selector. ex: "foo{bar:'baz'}"
            if '{' == self.lookahead(i).type:
                brace = True
            elif '}' == self.lookahead(i).type:
                brace = False
            if brace and ':' == self.lookahead(i).type:
                return True

            # '{' preceded by a space is considered a selector.
            # for example "foo{bar}{baz}" may be a property,
            # however "foo{bar} {baz}" is a selector
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
        if self.current_state() in ['root', 'atblock', 'selector',
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
        elif type in ['comment', 'selector', 'literal', 'charset',
                      'namespace', 'import', 'require', 'extend',
                      'media', 'atrule', 'ident', 'scope', 'supports',
                      'unless', 'function', 'for', 'if']:
            return self.__getattribute__(f'stmt_{type}')()
        elif type in 'return':
            return self.resturn()
        elif type == '{':
            return self.property()
        else:
            if self.state_allows_selectior():
                if type in ['color', '~', '>', '<', ':',
                            '&', '&&', '[', '.', '/']:
                    return self.selector()
                elif type == '..':
                    # relative reference
                    if '/' == self.lookahead(2).type:
                        return self.selector()
                elif type == '+':
                    if 'function' == self.lookahead(2).type:
                        return self.function_call()
                    else:
                        return self.selector()
                elif type == '*':
                    return self.property()
                elif type == 'unit':
                    if self.looks_like_keyframe():
                        return self.selector()
                elif type == '-':
                    if '{' == self.lookahead(2).type:
                        return self.property()

        expr = self.expression()
        if expr.is_empty():
            self.error('unexpected {peek}')
        return expr

    def ident(self):
        i = 2
        la = self.lookahead(i).type

        while 'space' == la:
            i += 1
            la = self.lookahead(i).type

        if la in ['=', '?=', '-=', '+=', '*=', '/=', '%=']:
            self.assignment()
        elif la == '.':
            # member
            if 'space' == self.lookahead(i - 1).type:
                return self.selector()
            if self._ident == self.peek():
                return self.id()
            i += 1
            while '=' != self.lookahead(i) and self.lookahead(i).type \
                    not in ['[', ',', 'newline', 'indent', 'eos']:
                pass
            if '=' == self.lookahead(i).type:
                self._indent = self.peek()
                return self.expression()
            elif self.looks_like_selector() and self.state_allows_selector():
                return self.selector()
        elif la == '[':
            # assignment []=
            if self._ident == self.peel():
                return self.id()
            i += 1
            while self.lookahead(i).type not in [']', 'selector', 'eos']:
                pass
            if '=' == self.lookahead(i).type:
                self._ident = self.peek()
                return self.expression()
            elif self.looks_like_selector() and self.state_allows_selector():
                return self.selector()
        elif la in ['-', '+', '/', '*', '%', '**', '&&', '||', '>', '<',
                    '>=', '<=', '!=', '==', '?', 'in', 'is a', 'is defined']:
            if self._ident == self.peek():
                # Prevent cyclic.ident, return literal
                return self.id()
            else:
                self._ident = self.peek()
                if self.current_state() in ['for', 'selector']:
                    # unary op or selector in property / for
                    return self.property()
                elif self.current_state() in ['root', 'atblock', 'atrule']:
                    # part of a selector
                    if la == '[':
                        self.subscript()
                    else:
                        self.selector()
                elif self.current_state() in ['function', 'conditional']:
                    if self.looks_like_selector():
                        return self.selector()
                    else:
                        return self.expression()
                else:
                    # do not disrupt the ident when an operand
                    if self.id():
                        return self.operand
                    else:
                        return self.expression()
        else:
            # selector or property
            if self.current_state() == 'root':
                return self.selector()
            elif self.current_state() in ['for', 'selector', 'function',
                                          'conditional', 'atblock', 'atrule']:
                return self.property()
            else:
                id = self.id()
                if self.previous_state() == 'interpolation':
                    id.mixin = true
                return id

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
            block.push(stmt)

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

    def stmt_comment(self):
        node = self.next().value
        self.skip_spaces()
        return node

    def stmt_for(self):
        # TODO: implement me!
        pass

    def selector(self):
        scope = self.selector_scope
        group = Group()
        is_root = self.current_state() == 'root'

        while True:
            self.accept('newline')  # clobber newline after ,
            arr = self.selector_parts()

            # push the selector
            if is_root and scope:
                arr.appendleft(Literal(f'{scope} '))
            if len(arr) > 0:
                selector = Selector(arr)
                selector.lineno = arr[0].lineno
                selector.column = arr[0].column
                group.push(selector)

            if (self.accept(',') or self.accept('newline')) is None:
                break

        if 'selector-parts' == self.current_state():
            return group.nodes

        self.state.append('selector')
        group.block = self.block(group)
        self.state.pop()

        return group

    def selector_parts(self) -> deque:
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
                    pass
                elif tok.type in ['color', 'unit']:
                    arr.append(Literal(tok.value.raw))
                elif tok.type == 'space':
                    arr.append(Literal(' '))
                elif tok.type == 'function':
                    arr.append(Literal(f'{tok.value.name}('))
                elif tok.type == 'ident':
                    # FIXME: string vs name?
                    arr.append(Literal(tok.value.string))
                else:
                    arr.append(Literal(tok.value))
                    if tok.space:
                        arr.append(Literal(' '))
            else:
                break
        print(arr)
        return arr

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
                return self.selector()
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
                return self.selector()
            else:
                # huh?
                pass
        elif la == '[':
            # assignment []=
            if self._indent == self.peek():
                return self._id()
            while ']' != self.lookahead(i).type and \
                    'selector' != self.lookahead(i) and \
                    'oes' != self.lookahead(i):
                i += 1
            if '=' == self.lookahead(i).type:
                self._indent = self.peek()
                return self.expression()
            elif self.looks_like_selector() and self.state_allows_selector():
                return self.selector()
        elif la in ['-', '+', '/', '*', '%', '**', '&&', '||', '>', '<', '>=',
                    '<=', '!=', '==', '?', 'in', 'is a', 'is defined']:
            # operation
            # prevent cyclic .ident, return literal
            if self._ident - - self.peek():
                return self.id()
            else:
                self._ident = self.peek()
                if self.current_state() in ['for', 'selector']:
                    return self.property()
                elif self.current_state() in ['root', 'atblock', 'atrule']:
                    if '[' == la:
                        return self.subscript()
                    else:
                        return self.selector()
                elif self.current_state() in ['function', 'conditional']:
                    if self.looks_like_selector():
                        return self.selector()
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
                return self.selector()
            elif self.current_state() in ['for', 'selector', 'function',
                                          'conditional', 'atblock', 'atrule']:
                return self.property()
            else:
                id = self.id()
                if 'interpolation' == self.previous_state():
                    id.mixin = True
                return id

    def property(self):
        if self.looks_like_selector(True):
            return self.selector()

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
        # TODO: add lineno and column
        expr = Expression()
        self.state.append('expression')
        while True:
            node = self.negation()
            if not node:
                self.error('unexpected token {peek} in expression')
            expr.push(node)
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
        node = self.expression()

        while True:
            next = self.accept(',')
            if next:
                if node.is_list:
                    list.append(self.expression())
                else:
                    list = Expression(true)
                    list.push(node)
                    list.push(self.expression())
                    node = list
            else:
                break

    def logical(self):
        node = self.typecheck()
        while True:
            if self.peek().type in ['&&', '||']:
                op = self.next()
                node = BinOp(op.type, node, self.typecheck())
            else:
                break

    def typecheck(self):
        node = self.equality()
        while True:
            if self.peek().type == 'is a':
                op = self.next()
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
            type = self.peek().type
            if type in ['==', '!=']:
                op = self.next()
                self.operand = True
                if not node:
                    self.error(f'illegal unary "{op}", '
                               f'missing left-hand operand')
                node = BinOp(op.type, node, self.inn())
            else:
                break

    def inn(self):
        node = self.relational()
        while True:
            type = self.peek().type
            if type == 'in':
                self.next()
                if not node:
                    self.error('illegal unary "in", '
                               'missing left-hand operand')
                node = BinOp('in', node, self.relational())
            else:
                break

    def relational(self):
        pass

    def function_call(self):
        pass
