import re
from collections import deque


class Token:

    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.space = None

    def __str__(self):
        space = f', space={self.space}' if self.space else ''
        return f'Token({self.type}, {self.value}{space})'

    def __repr__(self):
        return str(self)


class Lexer:
    alias = {'and': '&&',
             'or': '||',
             'is': '==',
             'isnt': '!=',
             'is not': '!=',
             ':=': '?='}

    def __init__(self, str, options=None):
        self.stash = deque([])
        self.indent_stack = deque([])
        self.indent_re = None
        self.lineno = 1
        self.column = 1

        self.prev = None
        self.is_url = False
        self.at_eos = False

        self.str = self.clean(str)
        # print(f'Lexing [{self.str}]...')

    def clean(self, str):
        str = str[1:] if "\uFEFF" == str[0] else str  # handle UTF-8 BOM

        str = re.sub(r'\s+$', '\n', str)
        str = re.sub(r'\r\n', '\n', str)

        return str

    def _comment(self, str, value, offset, s):
        pass

    def _skip_number(self, len):
        self.str = self.str[len:]

    def _skip_string(self, str):
        self.str = self.str[len(str):]

    def next(self) -> Token:
        tok = self.stash.popleft() if len(self.stash) > 0 else self.advance()
        self.prev = tok
        self.at_eos = tok.type == 'eos'
        return tok

    def __next__(self) -> Token:
        if self.at_eos:
            raise StopIteration
        return self.next()

    def __iter__(self):
        return self

    def advance(self):
        # print(f'advancing: {self.str}')
        tok = self.eos()
        if tok:
            return tok
        tok = self.null()
        if tok:
            return tok
        tok = self.newline()
        if tok:
            return tok
        tok = self.op()
        if tok:
            return tok
        tok = self.eol()
        if tok:
            return tok
        tok = self.space()
        if tok:
            return tok
        tok = self.selector()
        if tok:
            return tok
        return None

    def is_part_of_selector(self):
        tok = self.stash[-1] if self.stash else self.prev
        if tok and tok.type == 'color':
            return 2 == tok.value.raw.length
        elif tok and (tok.type in ['.', '[']):
            return True
        else:
            return False

    def eos(self):
        if self.str != '':
            return False
        if self.indent_stack:
            self.indent_stack.popleft()
            return Token('outdent')
        else:
            return Token('eos')

    def null(self):
        match = re.match(r'^(null)\b[ \t]*', self.str)
        if match:
            self._skip_string(match.group())
            if self.isPartOfSelector():
                return Token('indent', Ident)
            else:
                return Token('null')

    def newline(self):
        """
        '\n' ' '+
        """
        if self.indent_re:
            match = re.match(self.indent_re, self.str)

        # figure out if we are using tabs or spaces
        else:
            # try tabs first
            possible_re = r'^\n([\t]*)[ \t]*'
            match = re.match(possible_re, self.str)
            if not match or not match.group(1):
                # try spaces next
                possible_re = r'^\n([ \t]*)'
                match = re.match(possible_re, self.str)
            # established
            if match and match.group(1):
                self.indent_re = possible_re

        if match:
            indents = len(match.group(1))

            self._skip_string(match.group(0))

            if self.str and self.str[0] in [' ', '\t']:
                raise SyntaxError('Invalid indentation. You can use tabs or '
                                  'spaces to indent, but not both.')

            # blank line
            if self.str and self.str[0] == '\n':
                return self.advance()

            # outdent
            if self.indent_stack and indents < self.indent_stack[0]:
                while self.indent_stack and self.indent_stack[0] > indents:
                    self.stash.append(Token('outdent'))
                    self.indent_stack.popleft()
                tok = self.stash.pop()

            # indent
            elif indents and (len(self.indent_stack) == 0 or indents != self.indent_stack[0]):
                self.indent_stack.appendleft(indents)
                tok = Token('indent')

            # newline
            else:
                tok = Token('newline')

            return tok

        return False

    def selector(self):
        """
        ^|[^\n,;]+
        """
        match = re.match(r'^\^|.*?(?=\/\/(?![^\[]*\])|[,\n{])', self.str)
        if match and match.group(0):
            selector = match.group(0)
            self._skip_string(selector)
            return Token('selector', selector)

    def space(self):
        """
        ' '+ | '\t'+
        """
        match = re.match(r'^([ \t]+)', self.str)
        if match:
            self._skip_string(match.group(0))
            return Token('space')

    def eol(self):
        """
        '\n'
        """
        if self.str and self.str[0] == '\n':
            self.lineno += 1
            self._skip_number(1)
            return self.advance()

    def op(self):
        """
        ',' | '+' | '+=' | '-' |  '-=' |  '*' | '*=' | '/' | '/=' | '%' |
        '%=' | '**' |  '!' | '&' | '&&' | '||' | '>' | '>=' | '<' | '<=' |
        '=' | '==' | '!=' | '!' | '~' | '?=' | ':=' | '?' | ':' | '[' |
        ']' | '.' | '..' |'...'
        """
        match = re.match(r'^([.]{1,3}|&&|\|\||[!<>=?:]=|\*\*|[-+*\/%]=?|'
                         r'[,=?:!~<>&\[\]])([ \t]*)',
                         self.str)
        if match:
            op = match.group(0)
            self._skip_string(op)
            op = self.alias.get(op, op)
            tok = Token(op, op)
            tok.space = match.group(2)
            self.is_url = False
            return tok
