from stilus.lexer import Lexer, Token
from stilus.nodes.block import Block
from stilus.nodes.boolean import true
from stilus.nodes.each import Each
from stilus.nodes.it import If
from stilus.nodes.node import Node
from stilus.nodes.root import Root


class ParseError(Exception):
    pass


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

    def skip_whitespace(self):
        self.skip(['space', 'indent', 'outdent', 'newline'])

    def skip(self, tokens):
        while self.peek().type in tokens:
            self.next()

    def next(self) -> Token:
        tok = self.lexer.next()
        return tok

    def peek(self) -> Token:
        return self.lexer.peek()

    def accept(self, type):
        if self.peek().type == type:
            return self.next()

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
