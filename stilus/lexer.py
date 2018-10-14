import re
from collections import deque

from stilus.nodes.color import RGBA
from .nodes.comment import Comment
from .nodes.ident import Ident
from .nodes.literal import Literal


class Token:

    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        # extras
        self.space = None
        self.anonymous = False

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
        # handle UTF-8 BOM
        str = str[1:] if len(str) > 1 and "\uFEFF" == str[0] else str

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
        tok = self.sep()
        if tok:
            return tok
        tok = self.keyword()
        if tok:
            return tok
        tok = self.urlchars()
        if tok:
            return tok
        tok = self.comment()
        if tok:
            return tok
        tok = self.newline()
        if tok:
            return tok
        tok = self.escaped()
        if tok:
            return tok
        tok = self.important()
        if tok:
            return tok
        tok = self.literal()
        if tok:
            return tok
        tok = self.anonymous_function()
        if tok:
            return tok
        tok = self.atrule()
        if tok:
            return tok
        tok = self.function()
        if tok:
            return tok
        tok = self.brace()
        if tok:
            return tok
        tok = self.paren()
        if tok:
            return tok
        tok = self.color()
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
        """
        eos | trailing outdents
        """
        if self.str != '':
            return False
        if self.indent_stack:
            self.indent_stack.popleft()
            return Token('outdent')
        else:
            return Token('eos')

    def null(self):
        """
        null
        """
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
            elif indents and (len(self.indent_stack) == 0 or
                              indents != self.indent_stack[0]):
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

    def sep(self):
        """
        ';' [ \t]*
        """
        match = re.match(r'^;[ \t]*', self.str)
        if match:
            self._skip_string(match.group(1))
            return Token(';')

    def keyword(self):
        """
        'if' | 'else' | 'unless' | 'return' | 'for' | 'in'
        """
        match = re.match(r'^(return|if|else|unless|for|in)\b[ \t]*', self.str)
        if match:
            keyword = match.group(1)
            self._skip_string(keyword)
            if self.is_part_of_selector():
                tok = Token('ident', Ident(match.group(0)))
            else:
                tok = Token(keyword, keyword)
            return tok

    def urlchars(self):
        """
        url char
        """
        match = re.match(r'^[\/:@.;?&=*!,<>#%0-9]+', self.str)
        if match:
            self._skip_string(match.group(0))
            return Token('literal', Literal(match.group(0)))

    def comment(self):
        """
        '//' *
        """
        # single line
        if '/' == self.str[0] and '/' == self.str[1]:
            end = self.str.find('\n')
            if -1 == end:
                end = len(self.str)
            self._skip_number(end)
            return self.advance()

        # multi-line
        if '/' == self.str[0] and '*' == self.str[1]:
            end = self.str.find('*/')
            suppress = True
            inline = False
            s = self.str[0:end + 2]
            lines = len(re.split(r'[\n|\r]', s)) - 1
            self.lineno += lines
            self._skip_number(end + 2)
            # output
            if '!' == s[2]:
                s = s.replace('*!', '*')
                suppress = False
            if self.prev and ';' == self.prev.type:
                inline = True
            return Token('comment', Comment(s, suppress, inline))

    def escaped(self):
        """
        '\\' . ' '*
        """
        match = re.match(r'^\\(.)[ \t]*', self.str)
        if match:
            escape = match.group(1)
            self._skip_string(escape)
            return Token('ident', Literal(escape))

    def important(self):
        """
        '!important' ' '*
        """
        match = re.match(r'^!important[ \t]*', self.str)
        if match:
            self._skip_string(match.group(0))
            return Token('ident', Literal('!important'))

    def literal(self):
        """
        '@css' ' '* '{' .* '}' ' '*
        """
        match = re.match(r'^@css[ \t]*', self.str)
        if match:
            self._skip_string(match.group(0))
            braces = 1
            css = ''
            for c in self.str:
                print(f'Handling {c} in {self.str}]')
                if c == '{':
                    braces += 1
                elif c == '}':
                    braces -= 1
                elif c in ['\n', '\r']:
                    self.lineno += 1
                css += c
                if not braces:
                    break
            css = re.sub(r'\s*}$', '', css)  # hack?
            return Token('literal', Literal(css, css=True))

    def anonymous_function(self):
        """
        '@('
        """
        if '@' == self.str[0] and '(' == self.str[1]:
            self._skip_number(2)
            tok = Token('function', Ident('anonymous'))
            tok.anonymous = True
            return tok

    def atrule(self):
        """

        """
        match = re.match(r'^@(?:-(\w+)-)?([a-zA-Z0-9-_]+)[ \t]*', self.str)
        if match:
            self._skip_number(match.group(0))
            vendor = match.group(1)
            type = match.group(2)
            if type in ['require', 'import', 'charset', 'namespace',
                        'media', 'scope', 'supports']:
                return Token(type)
            elif type == 'document':
                return Token('-moz-document')
            elif type == 'block':
                return Token('atblock')
            elif type in ['extend', 'extends']:
                return Token('extend')
            elif type == 'keyframes':
                return Token(type, vendor)
            else:
                return Token('atrile', f'-{vendor}-{type}' if vendor else type)

    def function(self):
        """

        """
        match = re.match(r'^(-*[_a-zA-Z$][-\w\d$]*)\(([ \t]*)', self.str)
        if match:
            name = match.group(1)
            self._skip_string(match.group(0))
            self.is_url = 'url' == name
            tok = Token('function', Ident(name))
            tok.space = match.group(2)
            return tok

    def brace(self):
        """
        '{' | '}'
        """
        match = re.match(r'^([{}])', self.str)
        if match:
            self._skip_number(1)
            brace = match.group(1)
            return Token(brace, brace)

    def paren(self):
        """
        '(' | ')' ' '*
        """
        match = re.match(r'^([()])([ \t]*)', self.str)
        if match:
            paren = match.group(1)
            self._skip_string(match.group(0))
            if ')' == paren:
                self.is_url = False
            tok = Token(paren, paren)
            tok.space = match.group(2)
            return tok

    def rrggbbaa(self):
        """
        #rrggbbaa
        """
        match = re.match(r'^#([a-fA-F0-9]{8})[ \t]*', self.str)
        if match:
            self._skip_string(match.group(0))
            rgb = match.group(1)
            r = int(rgb[0:2], 16)
            g = int(rgb[2:4], 16)
            b = int(rgb[4:6], 16)
            a = int(rgb[6:8], 16)
            color = RGBA(r, g, b, a/255)
            color.raw = match.group(0)
            return Token('color', color)

    def color(self):
        raise NotImplementedError
