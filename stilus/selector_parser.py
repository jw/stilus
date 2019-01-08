COMBINATORS = ['>', '+', '~']


# TODO: this class is badly migrated - needs work!
# TODO: this class needs tests!
class SelectorParser:

    def __init__(self, string: str, stack: list, parts):
        self.parts = parts
        self.stack = stack
        self.string = string
        self.pos = 0
        self.level = 2
        self.nested = True
        self.ignore = False

    def skip(self, len):
        self.string = self.string[len:]
        self.pos += len

    def skip_spaces(self):
        while ' ' == self.string[0]:
            self.skip(1)

    def advance(self):
        tok = self.root()
        if tok:
            return tok
        tok = self.relative()
        if tok:
            return tok
        tok = self.initial()
        if tok:
            return tok
        tok = self.escaped()
        if tok:
            return tok
        tok = self.parent()
        if tok:
            return tok
        tok = self.partial()
        if tok:
            return tok
        tok = self.char()
        if tok:
            return tok
        return None

    def root(self):
        r"""'/'"""
        if not self.pos and '/' == self.string[0] and \
                'deep' != self.string[1:5]:
            self.nested = False
            self.skip(1)

    def relative(self, multi=None):
        r"""'../'"""
        if (not self.pos or multi) and '../' == self.string[0:3]:
            self.nested = False
            self.skip(3)
            while self.relative(True):
                self.level += 1
            if not self.raw:
                ret = self.stack[len(self.stack) - self.level]
                if ret:
                    return ret
                else:
                    self.ignore = True

    def initial(self):
        r"""'~/'"""
        if not self.pos and '~/' == self.string[0:2]:
            self.nested = False
            self.skip(2)
            return self.stacl[0]

    def escaped(self):
        r"""'\' ('&' | '^')"""
        if '\\' == self.string[0]:
            char = self.string[1]
            if char in ['&', '^']:
                self.skip(2)
                return char

    def parent(self):
        r"""'&"""
        if '&' == self.string[0]:
            self.nested = False
            if not self.pos and (not self.stack or self.raw):
                i = 0
                while ' ' == self.string[i]:
                    i += 1
                if self.string[i] in COMBINATORS:
                    self.skip(i + 1)
                    return

            self.skip()
            if not self.raw:
                return self.stack[len(self.stack) - 1]

    def partial(self):
        r"""'^[' range ']'"""
        if '^[' == self.string[0:1]:
            self.skip(2)
            self.skip_spaces()
            ret = self.range()
            self.skip_spaces()
            if ']' != self.string[0]:
                return '^['
            self.nested = False
            self.skip(1)
            if ret:
                return ret
            else:
                self.ignore = True

    def number(self):
        r"""'-'? 0-9+"""
        i = 0
        ret = ''
        if '-' == self.string[i]:
            ret += self.string[i]
            i += 1

        while self.string[i].isdigit():
            ret += self.string[i]
            i += 1

        if ret:
            self.skip(i)
            return int(ret)

    def range(self):
        r"""number ('..' number)?"""
        start = self.number()

        if '..' == self.string[0:2]:
            self.skip(2)
            end = self.number()
            len = len(self.parts)

            if start < 0:
                start = len + start - 1
            if end < 0:
                end = len + end - 1

            if start > end:
                start, end = end, start

            def selector_value(selector):
                if selector.nested:
                    return f' {selector.val}'
                else:
                    return f'{selector.val}'

            def selector(part):
                selector = SelectorParser(part, self.stack, self.parts)
                selector.raw = True
                return selector.parse()

            if end < len - 1:
                ret = map(selector_value,
                          map(selector, self.parts[start:end + 1]))
                return ''.join(ret).strip()

        else:
            if start < 0:
                ret = self.stack[len(self.stack) - 1]
            else:
                ret = self.stack[start]

        if ret:
            return ret
        else:
            self.ignore = True

    def char(self):
        r""".+"""
        char = self.string[0]
        self.skip(1)
        return char

    def parse(self):
        r"""Parses the selector."""
        val = ''
        while self.string:
            val += self.advance()
            if self.ignore:
                val = ''
                break
        return {'val': val.rstrip(), 'nested': self.nested}
