import re
from collections import deque


class Token:

    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {self.value})'

    def __repr__(self):
        return str(self)


class Lexer:

    def __init__(self, str, options=None):
        self.stash = deque([])
        self.indentStack = deque([])
        self.indentRe = None
        self.lineno = 1
        self.column = 1
        self.prev = None

        self.str = self.clean(str)

    def clean(self, str):
        str = str[1:] if "\uFEFF" == str[0] else str  # handle UTF-8 BOM

        str = re.sub(r'\s+', '\n', str)
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
        return tok

    def __next__(self) -> Token:
        next = self.next()
        if next:
            return next
        else:
            raise StopIteration

    def __iter__(self):
        return self

    def advance(self):
        # print(f'advancing: {self.str}')
        tok = self.selector()
        if tok:
            return tok
        tok = self.space()
        if tok:
            return tok
        tok = self.eol()
        if tok:
            return tok

        tok = self.null()
        if tok:
            return tok
        tok = self.eos()
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
        if not self.str:
            return False
        if self.indentStack:
            self.indentStack.popleft()
            return Token('outdent')
        else:
            return Token('eos')

    def null(self):
        match = re.match(r'^(null)\b[ \t]*', self.str)
        if match:
            self._skip_string(match.group())
            if self.isPartOfSelector():
                return Token('indent')
            else:
                return Token('null')

    def selector(self):
        match = re.match(r'^\^|.*?(?=\/\/(?![^\[]*\])|[,\n{])', self.str)
        if match and match.group(0):
            selector = match.group(0)
            self._skip_string(selector)
            return Token('selector', selector)

    def space(self):
        match = re.match(r'^([ \t]+)', self.str)
        if match:
            self._skip_string(match.group(0))
            return Token('space')

    def eol(self):
        if self.str and self.str[0] == '\n':
            self.lineno += 1
            self._skip_number(1)
            return self.advance()

