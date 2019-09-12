from collections import deque

from stilus.exceptions import ParseError
from stilus.lexer import Lexer, Token
from stilus.nodes.arguments import Arguments
from stilus.nodes.atblock import Atblock
from stilus.nodes.atrule import Atrule
from stilus.nodes.binop import BinOp
from stilus.nodes.block import Block
from stilus.nodes.boolean import true
from stilus.nodes.call import Call
from stilus.nodes.chartset import Charset
from stilus.nodes.each import Each
from stilus.nodes.expression import Expression
from stilus.nodes.extend import Extend
from stilus.nodes.feature import Feature
from stilus.nodes.function import Function
from stilus.nodes.group import Group
from stilus.nodes.ident import Ident
from stilus.nodes.ifnode import If
from stilus.nodes.import_node import Import
from stilus.nodes.keyframes import Keyframes
from stilus.nodes.literal import Literal
from stilus.nodes.media import Media
from stilus.nodes.member import Member
from stilus.nodes.namespace import Namespace
from stilus.nodes.node import Node
from stilus.nodes.nothing import Nothing
from stilus.nodes.null import null
from stilus.nodes.object_node import ObjectNode
from stilus.nodes.params import Params
from stilus.nodes.property import Property
from stilus.nodes.query import Query
from stilus.nodes.query_list import QueryList
from stilus.nodes.return_node import ReturnNode
from stilus.nodes.root import Root
from stilus.nodes.selector import Selector
from stilus.nodes.supports import Supports
from stilus.nodes.ternary import Ternary
from stilus.nodes.unaryop import UnaryOp
from stilus.units import units


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
        self.allow_postfix = None
        self.prev_state = None
        self.lineno = 1
        self.column = 1

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
        try:
            return self.state[-2]
        except Exception as e:
            # todo: handle this properly
            raise e

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
        if self.stash:
            tok = self.stash.pop()
        else:
            tok = self.lexer.next()
        if tok.value and isinstance(tok.value, Node):
            tok.value.lineno = tok.lineno
            tok.value.column = tok.column
        self.lineno = tok.lineno
        self.column = tok.column
        # todo: log this: print(tok)
        return tok

    def __iter__(self):
        return self

    def __next__(self):
        tok = self.next()
        if tok.type == 'eos':
            raise StopIteration
        return tok

    def peek(self) -> Token:
        return self.lexer.peek()

    def lookahead(self, n):
        return self.lexer.lookahead(n)

    def is_selector_token(self, n: int) -> bool:
        """
        Check if the token at n is a valid selector token.
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
            return value.value in self.pseudo_selectors

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
        return self.lookahead(i).type in ['indent', '{']

    def looks_like_selector(self, from_property=False):
        i = 1

        # real property
        if from_property and ':' == self.lookahead(i + 1).type and \
                (self.lookahead(i + 1).space or
                 'indent' == self.lookahead(i + 2).type):
            return False

        # assume selector when an ident is followed by a selector
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
            brace = None
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
            if ':' == self.lookahead(i - 1).type and \
                    not self.lookahead(i - 1).space and \
                    self.is_pseudo_selector(i):
                return True

            # trailing space
            if 'space' == self.lookahead(i).type and \
                    'newline' == self.lookahead(i + 1).type and \
                    '{' == self.lookahead(i + 2).type:
                return True

            if ',' == self.lookahead(i).type and \
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
        if self.css > 0 and (';' == self.lookahead(i).type or
                             '}' == self.lookahead(i - 1).type):
            return False

        # trailing separators
        while self.lookahead(i).type not in ['indent', 'outdent', 'newline',
                                             'for', 'if', ';', '}', 'eos']:
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
            i += 1
            while self.lookahead(i).type in ['unit', 'newline']:
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
            expr.append(self.atblock(expr))
        except Exception:
            self.error(
                'invalid right-hand side operand in assignment, got {peek}')

    def statement(self):
        stmt = self.stmt()
        state = self.prev_state

        # special-case statements since it
        # is not an expression. We could
        # implement postfix conditionals at
        # the expression level, however they
        # would then fail to enclose properties
        if self.allow_postfix:
            self.allow_postfix = False
            state = 'expression'

        if state in ['assignment', 'expression', 'function arguments']:
            while True:
                op = self.accept(['if', 'unless', 'for'])
                if op and op.type in ['if', 'unless']:
                    stmt = If(self.expression(), stmt, lineno=self.lineno,
                              column=self.column)
                    stmt.postfix = true
                    stmt.negate = 'unless' == op.type
                    self.accept(';')
                elif op and op.type == 'for':
                    val = self.id().name
                    key = None
                    if self.accept(','):
                        key = self.id().name
                    self.expect('in')
                    each = Each(val, key, self.expression())
                    block = Block(self.parent, each,
                                  lineno=self.lineno, column=self.column)
                    block.append(stmt)
                    each.block = block
                    stmt = each
                else:
                    break
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
            return self.return_expression()
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
                        return self.function_call()
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

    def stmt_literal(self):
        return self.expect('literal').value

    def stmt_charset(self):
        self.expect('charset')
        str = self.expect('string').value
        self.allow_postfix = True
        return Charset(str)

    def stmt_namespace(self):
        self.expect('namespace')
        self.skip_spaces_and_comments()
        prefix = self.accept('ident')
        if prefix:
            prefix = prefix.value
        self.skip_spaces_and_comments()

        str = self.accept('string')
        if str is not None:
            str = self.url()
        self.allow_postfix = True
        return Namespace(str, prefix)

    def stmt_import(self):
        self.expect('import')
        self.allow_postfix = True
        return Import(self.expression(), False,
                      lineno=self.lineno, column=self.column)

    def stmt_require(self):
        self.expect('require')
        self.allow_postfix = True
        return Import(self.expression(), True,
                      lineno=self.lineno, column=self.column)

    def stmt_extend(self):
        tok = self.expect('extend')
        selectors = []
        try:
            while True:
                arr = self.selector_parts()
                if arr is None or len(arr) == 0:
                    if self.accept(';'):
                        continue
                    else:
                        raise TypeError
                sel = Selector(arr)
                selectors.append(sel)

                if self.peek().type != '!':
                    if self.accept(';'):
                        continue
                    else:
                        raise TypeError

                tok = self.lookahead(2)
                if tok.type not in ['ident', 'optional']:
                    continue
                self.skip(['!', 'ident'])
                sel.optional = True
                token = self.accept(',')
                if token is None:
                    break
        except TypeError:
            pass

        node = Extend(selectors)
        node.lineno = tok.lineno
        node.column = tok.column
        return node

    def stmt_media(self):
        self.expect('media')
        self.state.append('atrule')
        media = Media(self.queries())
        media.block = self.block(media)
        self.prev_state = self.state[-1]
        self.state.pop()
        return media

    def queries(self):
        queries = QueryList()
        while True:
            self.skip(['comment', 'newline', 'space'])
            queries.append(self.query())
            self.skip(['comment', 'newline', 'space'])
            if not self.accept(','):
                break
        return queries

    def query(self):
        query = Query()

        # hash values support
        if self.peek().type == 'ident' and \
                (self.lookahead(2).type == '.' or
                 self.lookahead(2).type == '['):
            self.cond = True
            expr = self.expression()
            self.cond = False
            query.append(Feature(expr.nodes))
            return query

        pred = self.accept(['ident', 'not'])
        if pred:
            if pred.value.string:
                pred = Literal(pred.value.string,
                               lineno=self.lineno,
                               column=self.lineno)
            else:
                pred = pred.value

            self.skip_spaces_and_comments()
            id = self.accept('ident')
            if id:
                query.type = id.value
                query.predicate = pred
            else:
                query.type = pred
            self.skip_spaces_and_comments()

            if self.accept('&&') is None:
                return query

        while True:
            query.append(self.feature())
            if self.accept('&&') is None:
                break

        return query

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

    def stmt_atrule(self):
        type = self.expect('atrule')
        node = Atrule(type)
        self.skip_spaces_and_comments()
        node.segments = self.selector_parts()
        self.skip_spaces_and_comments()
        tok = self.peek().type
        if tok in ['indent', '{'] or \
                (tok == 'newline' and self.lookahead(2).type == '{'):
            self.state.append('atrule')
            node.block = self.block(node)
            self.prev_state = self.state[-1]
            self.state.pop()
        return node

    def stmt_scope(self):
        self.expect('scope')
        selector = ''.join(map(lambda s: s.value, self.selector_parts()))
        self.selector_scope = selector.strip()
        return null

    def stmt_supports(self):
        self.expect('supports')
        node = Supports(self.supports_condition())
        self.state.append('atrule')
        node.block = self.block(node)
        self.prev_state = self.state[-1]
        self.state.pop()
        return node

    def supports_condition(self):
        node = self.supports_negation()
        if node is None:
            node = self.supports_op()
        if not node:
            self.cond = True
            node = self.expression()
            self.cond = False
        return node

    def supports_op(self):
        feature = self.supports_feature()
        if feature:
            expr = Expression(lineno=self.lineno, column=self.column)
            expr.append(feature)
            op = self.accept(['&&', '||'])
            while op:
                expr.append(Literal('and' if op.value == '&&' else '||',
                                    lineno=self.lineno,
                                    column=self.column))
                expr.append(self.supports_feature())
                op = self.accept(['&&', '||'])
            return expr
        return None

    def supports_negation(self):
        tok = self.accept('not')
        if tok:
            node = Expression(lineno=self.lineno, column=self.column)
            node.append(Literal('not', lineno=self.lineno, column=self.column))
            node.append(self.supports_feature())
            return node
        return None

    def supports_feature(self):
        self.skip_spaces_and_comments()
        if self.peek().type == '(':
            la = self.lookahead(2).type
            if la in ['ident', '{']:
                return self.feature()
            else:
                self.expect('{')
                node = Expression(lineno=self.lineno, column=self.column)
                node.append(Literal('{',
                                    lineno=self.lineno,
                                    column=self.column))
                node.append(self.supports_condition())
                self.expect(')')
                self.skip_spaces_and_comments()
                return node
        return None

    def stmt_unless(self):
        self.expect('unless')
        self.state.append('conditional')
        self.cond = True
        node = If(self.expression(), True, lineno=self.lineno,
                  column=self.column)
        self.cond = False
        node.block = self.block(node, False)
        self.prev_state = self.state[-1]
        self.state.pop()
        return node

    def stmt_for(self):
        self.expect('for')
        value = self.id().name
        key = None
        if self.accept(','):
            key = self.id().name
        self.expect('in')
        self.state.append('for')
        self.cond = True
        each = Each(value, key, self.expression())
        self.cond = False
        each.block = self.block(each, False)
        self.prev_state = self.state[-1]
        self.state.pop()
        return each

    def stmt_if(self):
        self.expect('if')
        self.state.append('conditional')
        self.cond = True
        node = If(self.expression(), lineno=self.lineno, column=self.column)
        self.cond = False
        node.block = self.block(node, False)
        self.skip(['newline', 'comment'])
        while self.accept('else'):
            if self.accept('if'):
                self.cond = True
                cond = self.expression()
                self.cond = False
                block = self.block(node, False)
                node.elses.append(If(cond, block,
                                     lineno=self.lineno, column=self.column))
            else:
                node.elses.append(self.block(node, False))
                break
            self.skip(['newline', 'comment'])
        self.prev_state = self.state[-1]
        self.state.pop()
        return node

    def block(self, node, scope=None):
        block = self.parent = Block(self.parent, node,
                                    lineno=self.lineno, column=self.column)

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
            if self.css > 0:
                if self.accept(['newline', 'indent']):
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
                    continue
                if 'eos' == self.peek().type:
                    return block
                stmt = self.statement()
                self.accept(';')
            if not stmt:
                self.error('unexpected token {peek} in block')
            block.append(stmt)

        # css-style
        if self.css > 0:
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
        group = Group(lineno=self.lineno, column=self.column)
        is_root = self.current_state() == 'root'

        while True:
            self.accept('newline')  # clobber newline after ','
            arr = self.selector_parts()

            # push the selector
            if is_root and scope:
                arr.appendleft(Literal(f'{scope} ',
                                       lineno=self.lineno,
                                       column=self.column))
            if len(arr) > 0:
                selector = Selector(arr)
                selector.lineno = arr[0].lineno
                selector.column = arr[0].column
                group.append(selector)

            if self.accept([',', 'newline']) is None:
                break

        if 'selector-parts' == self.current_state():
            return group.nodes

        self.state.append('selector')
        group.block = self.block(group)
        self.prev_state = self.state[-1]
        self.state.pop()

        return group

    def selector_parts(self) -> deque:
        """Selector candidates, stitched together to form a selector."""
        arr = deque()
        while True:
            tok = self.selector_token()
            if tok:
                if tok.type == '{':
                    self.skip_spaces()
                    expr = self.expression()
                    self.skip_spaces()
                    self.expect('}')
                    arr.append(expr)
                elif tok.type == self.prefix and '.':
                    literal = Literal(tok.value + self.prefix,
                                      lineno=self.lineno,
                                      column=self.column)
                    literal.prefixed = True
                    arr.append(literal)
                elif tok.type == 'comment':
                    # ignore comments
                    pass
                elif tok.type in ['color', 'unit']:
                    arr.append(Literal(tok.value.raw,
                                       lineno=self.lineno,
                                       column=self.column))
                elif tok.type == 'space':
                    arr.append(Literal(' ',
                                       lineno=self.lineno,
                                       column=self.column))
                elif tok.type == 'function':
                    arr.append(Literal(f'{tok.value.node_name}(',
                                       lineno=self.lineno,
                                       column=self.column))
                elif tok.type == 'ident':
                    if hasattr(tok.value, 'name') and tok.value.name:
                        arr.append(Literal(f'{tok.value.name}',
                                           lineno=self.lineno,
                                           column=self.column))
                    else:
                        arr.append(Literal(f'{tok.value.string}',
                                           lineno=self.lineno,
                                           column=self.column))
                else:
                    arr.append(Literal(tok.value,
                                       lineno=self.lineno,
                                       column=self.column))
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
            self.prev_state = self.state[-1]
            self.state.pop()

            if op.type == '?=':
                defined = BinOp('is defined', node)
                lookup = Expression(lineno=self.lineno, column=self.column)
                lookup.append(Ident(name))
                node = Ternary(defined, lookup, node)
            elif op.type in ['+=', '-=', '*=', '/=', '%=']:
                node.value = BinOp(op.type[0], Ident(name), expr)

        return node

    def stmt_ident(self):
        i = 2
        la = self.lookahead(i).type

        while 'space' == la:
            i += 1
            la = self.lookahead(i).type

        go_on = False

        if la in ['=', '?=', '-=', '+=', '*=', '/=', '%=']:
            # assignment
            return self.assignment()

        if la == '.':
            # member
            if 'space' == self.lookahead(i - 1).type:
                return self.stmt_selector()
            if self._ident == self.peek():
                return self.id()
            while '=' != self.lookahead(i).type and \
                    self.lookahead(i + 1).type not in \
                    ['[', ',', 'newline', 'indent', 'eos']:

                i = i + 1
                pass
            i = i + 1
            if '=' == self.lookahead(i).type:
                self._ident = self.peek()
                return self.expression()
            elif self.looks_like_selector() and \
                    self.state_allows_selector():
                return self.stmt_selector()
            else:
                go_on = True

        if la == '[' or go_on:
            # assignment []=
            if self._ident == self.peek():
                return self.id()
            while ']' != self.lookahead(i).type and \
                    'selector' != self.lookahead(i + 1).type and \
                    'eos' != self.lookahead(i + 1).type:
                i += 1
            i += 1
            if '=' == self.lookahead(i).type:
                self._ident = self.peek()
                return self.expression()
            elif self.looks_like_selector() and self.state_allows_selector():
                return self.stmt_selector()
            go_on = True

        # operation
        if la in ['-', '+', '/', '*', '%', '**', '&&', '||', '>', '<', '>=',
                  '<=', '!=', '==', '?', 'in', 'is a', 'is defined'] or go_on:
            if self._ident == self.peek():
                return self.id()
            else:
                self._ident = self.peek()
                if self.current_state() in ['for', 'selector']:
                    return self.property()
                if self.current_state() in ['root', 'atblock', 'atrule']:
                    if la == ']':
                        return self.subscript()
                    else:
                        return self.stmt_selector()
                if self.current_state() in ['function', 'conditional']:
                    if self.looks_like_selector():
                        return self.stmt_selector()
                    else:
                        return self.expression()
                if self.operand:
                    return self.id()
                else:
                    return self.expression()

        if self.current_state() == 'root':
            return self.stmt_selector()
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
            return self.stmt_selector()

        # property
        ident = self.interpolate()
        prop = Property(ident, lineno=self.lineno, column=self.column)
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
        self.prev_state = self.state[-1]
        self.state.pop()

        # optional ';'
        self.accept(';')

        return ret

    def interpolate(self):
        node = None
        segs = []

        star = self.accept('*')
        if star:
            segs.append(Literal('*', lineno=self.lineno, column=self.column))

        while True:
            if self.accept('{'):
                self.state.append('interpolation')
                segs.append(self.expression())
                self.expect('}')
                self.prev_state = self.state[-1]
                self.state.pop()
            elif self.accept('-'):
                segs.append(Literal('-',
                                    lineno=self.lineno,
                                    column=self.column))
            else:
                node = self.accept('ident')
                if node:
                    segs.append(node.value)
                else:
                    break

        # empty segment list
        if len(segs) == 0:
            self.expect('ident')

        return segs

    # fixme!
    def expression(self):
        """negation+"""
        expr = Expression(lineno=self.lineno, column=self.column)
        self.state.append('expression')
        while True:
            node = self.negation()
            if node is None:
                self.error('unexpected token {peek} in expression')
            if node.node_name == 'nothing':
                break
            expr.append(node)
        self.prev_state = self.state[-1]
        self.state.pop()
        if len(expr.nodes) > 0:
            expr.lineno = expr.nodes[0].lineno
            expr.column = expr.nodes[0].column
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
                # todo: fixme was list, now node
                node.append(self.expression())
            else:
                list = Expression(true, lineno=self.lineno, column=self.column)
                list.append(node)
                list.append(self.expression())
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
            node = BinOp(op.type, node, self.range())
            self.operand = False
        return node

    def stmt_function(self):
        parens = 1
        i = 2

        # Lookahead and determine if we are dealing
        # with a function call or definition. Here
        # we pair parens to prevent false negatives

        try:
            tok = self.lookahead(i)
            i += 1
            while tok:
                if tok.type in ['function', '(']:
                    parens += 1
                    break
                elif tok.type == ')':
                    if parens - 1 == 0:
                        raise TypeError
                    break
                elif tok.type == 'oes':
                    self.error('failed to find closing paren ")"')
                tok = self.lookahead(i)
                i += 1
        except TypeError:
            pass

        if self.current_state() == 'expression':
            return self.function_call()
        else:
            if self.looks_like_function_definition(i):
                return self.function_definition()
            else:
                return self.expression()

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
        while op:
            self.operand = True
            node = BinOp(op.type, node, self.multiplicative())
            self.operand = False
            op = self.accept(['+', '-'])
        return node

    def multiplicative(self):
        node = self.defined()
        op = self.accept(['**', '*', '/', '%'])
        if op:
            self.operand = True
            if '/' == op.value and self.in_property and self.parens == 0:
                self.stash.append(Token('literal',
                                        Literal('/',
                                                lineno=self.lineno,
                                                column=self.column)))
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
        if node or node.node_name == 'null':  # todo: this seems not right
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
                return self.function_definition()
            else:
                return self.function_call()

        return Nothing()

    def function_definition(self):
        name = self.expect('function').value.name

        # params
        self.state.append('function params')
        self.skip_whitespace()
        params = self.params()
        self.skip_whitespace()
        self.expect(')')
        self.prev_state = self.state[-1]
        self.state.pop()

        # body
        self.state.append('function')
        fn = Function(name, params, lineno=self.lineno, column=self.column)
        fn.block = self.block(fn)
        self.prev_state = self.state[-1]
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

    def return_expression(self):
        self.expect('return')
        expr = self.expression()
        if expr.is_empty():
            return ReturnNode()
        else:
            return ReturnNode(expr)
        pass

    def keyframes(self):
        tok = self.expect('keyframes')
        self.skip_spaces_and_comments()
        keyframes = Keyframes(self.selector_parts(), tok.value)
        self.skip_spaces_and_comments()

        # block
        self.state.append('atrule')
        keyframes.block = self.block(keyframes)
        self.prev_state = self.state[-1]
        self.state.pop()

        return keyframes

    def args(self):
        args = Arguments()
        while True:
            if self.peek().type == 'ident' and self.lookahead(2).type == ':':
                keyword = self.next().value.string
                self.expect(':')
                args.map[keyword] = self.expression()
            else:
                args.append(self.expression())
            if self.accept(',') is None:
                break
        return args

    def url(self):
        self.expect('function')
        self.state.append('function')
        args = self.args()
        self.expect(')')
        self.prev_state = self.state[-1]
        self.state.pop()
        return Call('url', args, lineno=self.lineno, column=self.column)

    def mozdocument(self):
        self.expect('-moz-document')
        mozdocument = Atrule('-moz-document')
        calls = []
        while True:
            self.skip_spaces_and_comments()
            calls.append(self.function_call())
            self.skip_spaces_and_comments()
            if self.accept(',') is None:
                break
        mozdocument.segments = [Literal(', '.join(calls),
                                        lineno=self.lineno,
                                        column=self.column)]
        self.state.append('atrule')
        mozdocument.block = self.block(mozdocument, False)
        self.prev_state = self.state[-1]
        self.state.pop()
        return mozdocument

    def function_call(self):
        with_block = self.accept('+')
        if self.peek().value.name == 'url':
            return self.url()
        name = self.expect('function').value.name
        self.state.append('function arguments')
        self.parens += 1
        args = self.args()
        self.expect(')')
        self.parens -= 1
        self.prev_state = self.state[-1]
        self.state.pop()
        call = Call(name, args, lineno=self.lineno, column=self.column)
        if with_block:
            self.state.append('function')
            call.block = self.block(call)
            self.prev_state = self.state[-1]
            self.state.pop()
        return call

    def params(self):
        params = Params()
        tok = self.accept('ident')
        while tok:
            self.accept('space')
            node = tok.value
            params.append(node)
            if self.accept('...'):
                node.rest = True
            elif self.accept('='):
                node.value = self.expression()
            self.skip_whitespace()
            self.accept(',')
            self.skip_whitespace()
            tok = self.accept('ident')
        params.lineno = self.lineno
        params.column = self.column
        return params

    def object(self):
        comma = None
        obj = ObjectNode({})
        self.expect('{')
        self.skip_whitespace()

        while True:
            token = self.next()
            if token and token.type == '}':
                break
            if token.type in ['comment', 'newline']:
                continue
            if not comma and token.type == ',':
                continue
            if token.type in ['ident', 'string']:
                id = token
            if id is None:
                self.error('expected "ident" or "string", got {peek}')
            id = id.value.hash()
            self.skip_spaces_and_comments()
            self.expect(':')
            value = self.expression()
            obj.set(id, value)
            comma = self.accept(',')
            self.skip_whitespace()

        return obj

    def _operation(self, la):
        # operation
        # prevent cyclic .ident, return literal
        if self._ident == self.peek():
            return self.id()
        else:
            self._ident = self.peek()
            if self.current_state() in ['for', 'selector']:
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
                    return self.id()
                else:
                    return self.expression()
