COMBINATORS = ['>', '+', '~']


# TODO: this class is badly migrated - needs work!
# TODO: this class needs tests!
# TODO: this class needs proper getter and setters annotations!
class SelectorParser:

    def __init__(self, string: str, stack=None, parts=None):
        self.string = string
        self.stack = stack
        if stack is None:
            self.stack = []
        self.parts = parts
        if parts is None:
            self.parts = []
        self.pos = 0
        self.level = 2
        self.nested = True
        self.ignore = False
        self.value = None
        self.raw = False

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
                if len(self.stack) >= self.level:
                    return self.stack[len(self.stack) - self.level]
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

    # fixme: add the raw attribute/function check
    def parent(self):
        r"""'&"""
        if '&' == self.string[0]:
            self.nested = False
            if not self.pos and (not self.stack or self.raw):
                i = 0
                for i, char in enumerate(self.string[1:], start=1):
                    if char != ' ':
                        break
                if self.string[i] in COMBINATORS:
                    self.skip(i + 1)
                    return

            self.skip(1)
            # if not self.raw
            if self.stack and len(self.stack) > 0:
                return self.stack[len(self.stack) - 1]
            else:
                return None

    def partial(self):
        r"""'^[' range ']'"""
        if '^[' == self.string[0:2]:
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
        ret = None

        if '..' == self.string[0:2]:
            self.skip(2)
            end = self.number()
            length = len(self.parts)

            if start < 0:
                start = length + start - 1
            if end < 0:
                end = length + end - 1

            if start > end:
                start, end = end, start

            def selector_value(selector):
                if selector['nested']:
                    return f" {selector['value']}"
                else:
                    return f"{selector['value']}"

            def selector(part):
                selector = SelectorParser(part, self.stack, self.parts)
                selector.raw = True
                return selector.parse()

            if end < length - 1:
                ret = []
                for part in self.parts[start:end + 1]:
                    s = selector(part)
                    ret.append(selector_value(s))
                return ''.join(ret).strip()

        else:
            if len(self.stack) > 0:
                if start < 0:
                    ret = self.stack[len(self.stack) - 1]
                else:
                    ret = self.stack[start]
            else:
                ret = None
        if ret:
            return ret
        else:
            self.ignore = True

    def char(self):
        r""".+"""
        char = None
        if self.string:
            char = self.string[0]
        self.skip(1)
        return char

    def parse(self):
        r"""Parses the selector."""
        value = ''
        while self.string:
            next = self.advance()
            if next:
                value += next
            if self.ignore:
                value = ''
                break
        return {'value': value.rstrip(), 'nested': self.nested}
