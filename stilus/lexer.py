import re
from collections import deque

from stilus.nodes.boolean import Boolean
from stilus.nodes.color import RGBA
from stilus.nodes.null import null
from stilus.nodes.string import String
from stilus.nodes.unit import Unit
from .nodes.comment import Comment
from .nodes.ident import Ident
from .nodes.literal import Literal


class Token:

    def __init__(self, type, value=None, space=None, lineno=None, column=None):
        self.type = type
        self.value = value
        self.space = space
        self.anonymous = False
        self.lineno = lineno
        self.column = column

    def __str__(self):
        space = f', space={self.space}' if self.space else ''
        return f'Token({self.type}, {self.value}{space}) ' \
            f'[{self.lineno}:{self.column}]'

    def __repr__(self):
        return str(self)

    def __key(self):
        return self.type, self.value, self.space, self.anonymous, \
               self.lineno, self.column

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.__key() == other.__key()
        return False


class Lexer:
    alias = {'and': '&&',
             'or': '||',
             'is': '==',
             'isnt': '!=',
             'is not': '!=',
             ':=': '?='}

    def __init__(self, s: str, options: dict):
        self.stash = deque([])
        self.indent_stack = deque([])
        self.indent_re = None
        self.lineno = 1
        self.column = 1
        self.options = options

        self.prev = None
        self.is_url = False
        self.at_eos = False

        self.s = self.clean(s)

    def __eq__(self, other):
        if isinstance(other, Lexer):
            return self.s == other.s and self.options == other.options
        return False

    def clean(self, s: str) -> str:
        # handle UTF-8 BOM
        s = s[1:] if len(s) > 1 and "\uFEFF" == s[0] else s

        s = re.sub(r'\s+$', '\n', s)
        s = re.sub(r'\r\n?', '\n', s)
        s = re.sub(r'\\ *\n', '\r', s)
        # s = re.sub('\\[+]')

        def _comment(match):
            # TODO: this needs a cleanup
            s = match.group(0)
            value = match.groups()[0]
            offset = match.start(0)
            string = match.string
            in_comment = s.rfind('/*', offset) > s.rfind('*/', offset)
            comment_index = s.rfind('//', offset)
            i = s.rfind('\n', offset)
            double = 0
            single = 0

            if comment_index != -1 and comment_index > i:
                while i != offset:
                    if "'" == s[i]:
                        single = single - 1 if single else single + 1
                    if '"' == s[i]:
                        double = double - 1 if double else double + 1
                    if '/' == s[i] and '/' == s[i + 1]:
                        in_comment = not single and not double
                        break
                    i += 1

            return string if in_comment else value + '\r'

        s = re.sub(r'([,(:](?!\/\/[^ ])) *(?:\/\/[^\n]*|\/\*.*?\*\/)?\n\s*',
                   _comment, s)
        s = re.sub(r'\s*\n[ \t]*([,)])', _comment, s)

        return s

    def _skip_number(self, len):
        self.s = self.s[len:]
        self.column += len

    def _skip_string(self, str):
        self.s = self.s[len(str):]
        self.move(str)

    def move(self, str):
        lines = str.count('\n')
        self.lineno += lines
        idx = str.rfind('\n')
        if idx == -1:
            self.column += len(str)
        else:
            self.column = len(str) - idx

    def is_part_of_selector(self):
        tok = self.stash[-1] if self.stash else self.prev
        if tok and tok.type == 'color':
            return 2 == len(tok.value.raw)
        elif tok and (tok.type in ['.', '[']):
            return True
        else:
            return False

    def next(self) -> Token:
        tok = self.stash.popleft() if len(self.stash) > 0 else self.advance()
        self.prev = tok
        self.at_eos = tok.type == 'eos'
        return tok

    def peek(self):
        return self.lookahead(1)

    def lookahead(self, n):
        fetch = n - len(self.stash)
        while fetch > 0:
            fetch -= 1
            self.stash.append(self.advance())
        n -= 1
        return self.stash[n]

    def __next__(self) -> Token:
        if self.at_eos:
            raise StopIteration
        return self.next()

    def __iter__(self):
        return self

    # todo: use a dict to clean this up?
    def advance(self):
        lineno = self.lineno
        column = self.column
        tok = self.eos()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.null()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.sep()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.keyword()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.urlchars()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.comment()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.newline()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.escaped()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.important()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.literal()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.anonymous_function()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.atrule()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.function()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.brace()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.paren()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.color()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.string()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.unit()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.namedop()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.boolean()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.unicode()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.ident()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.op()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.eol()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.space()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        tok = self.selector()
        if tok:
            return self._tok_with_location(tok, lineno, column)
        return None

    def eos(self):
        """
        eos | trailing outdents
        """
        if self.s != '':
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
        match = re.match(r'^(null)\b[ \t]*', self.s)
        if match:
            self._skip_string(match.group())
            if self.is_part_of_selector():
                return Token('ident', Ident(match.group(0)))
            else:
                return Token('null', value=null)

    def newline(self):
        """
        '\n' ' '+
        """
        if self.indent_re:
            match = re.match(self.indent_re, self.s)

        # figure out if we are using tabs or spaces
        else:
            # try tabs first
            possible_re = r'^\n([\t]*)[ \t]*'
            match = re.match(possible_re, self.s)
            if match and not match.group(1):
                # try spaces next
                possible_re = r'^\n([ \t]*)'
                match = re.match(possible_re, self.s)
            # established
            if match and match.group(1):
                self.indent_re = possible_re

        if match:
            indents = len(match.group(1))

            self._skip_string(match.group(0))

            if self.s and self.s[0] in [' ', '\t']:
                raise SyntaxError('Invalid indentation. You can use tabs or '
                                  'spaces to indent, but not both.')

            # blank line
            if self.s and self.s[0] == '\n':
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
        match = re.match(r'^\^|.*?(?=\/\/(?![^\[]*\])|[,\n{])', self.s)
        if match and match.group(0):
            selector = match.group(0)
            self._skip_string(selector)
            return Token('selector', selector)

    def space(self):
        """
        ' '+ | '\t'+
        """
        match = re.match(r'^([ \t]+)', self.s)
        if match:
            self._skip_string(match.group(0))
            return Token('space')

    def eol(self):
        """
        '\r'
        """
        if self.s and self.s[0] == '\r':
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
                         self.s)
        if match:
            op = match.group(1)
            self._skip_string(match.group(0))
            op = self.alias.get(op, op)
            tok = Token(op, op)
            tok.space = match.group(2)
            self.is_url = False
            return tok

    def sep(self):
        """
        ';' [ \t]*
        """
        match = re.match(r'^;[ \t]*', self.s)
        if match:
            self._skip_string(match.group(0))
            return Token(';')

    def keyword(self):
        """
        'if' | 'else' | 'unless' | 'return' | 'for' | 'in'
        """
        match = re.match(r'^(return|if|else|unless|for|in)\b[ \t]*', self.s)
        if match:
            keyword = match.group(1)
            self._skip_string(match.group(0))
            if self.is_part_of_selector():
                tok = Token('ident', Ident(match.group(0)))
            else:
                tok = Token(keyword, keyword)
            return tok

    def urlchars(self):
        """
        url char
        """
        if not self.is_url:
            return
        match = re.match(r'^[\/:@.;?&=*!,<>#%0-9]+', self.s)
        if match:
            self._skip_string(match.group(0))
            return Token('literal', Literal(match.group(0)))

    def comment(self):
        """
        '//' *
        """
        # single line
        if '/' == self.s[0] and '/' == self.s[1]:
            end = self.s.find('\n')
            if -1 == end:
                end = len(self.s)
            self._skip_number(end)
            return self.advance()

        # multi-line
        if '/' == self.s[0] and '*' == self.s[1]:
            end = self.s.find('*/')
            suppress = True
            inline = False
            s = self.s[0:end + 2]
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
        match = re.match(r'^\\(.)[ \t]*', self.s)
        if match:
            escape = match.group(1)
            self._skip_string(match.group(0))
            if match.group(0).startswith('\\.'):
                escape = '\\.'
            return Token('ident', Literal(escape))

    def important(self):
        """
        '!important' ' '*
        """
        match = re.match(r'^!important[ \t]*', self.s)
        if match:
            self._skip_string(match.group(0))
            return Token('ident', Literal('!important'))

    def literal(self):
        """
        '@css' ' '* '{' .* '}' ' '*
        """
        match = re.match(r'^@css[ \t]*', self.s)
        if match:
            self._skip_string(match.group(0))
            braces = 1
            css = ''
            for c in self.s:
                if c == '{':
                    braces += 1
                elif c == '}':
                    braces -= 1
                elif c in ['\n', '\r']:
                    self.lineno += 1
                css += c
                if not braces:
                    break
            css = re.sub(r'\s*}$', '', css)
            return Token('literal', Literal(css, css=True))

    def anonymous_function(self):
        """
        '@('
        """
        if '@' == self.s[0] and '(' == self.s[1]:
            self._skip_number(2)
            tok = Token('function', Ident('anonymous'))
            tok.anonymous = True
            return tok

    def atrule(self):
        r"""
        # '@' (-(\w+)-)?[a-zA-Z0-9-_]+
        """
        match = re.match(r'^@(?:-(\w+)-)?([a-zA-Z0-9-_]+)[ \t]*', self.s)
        if match:
            self._skip_string(match.group(0))
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
                return Token('atrule', f'-{vendor}-{type}' if vendor else type)

    def function(self):
        r"""
         -*[_a-zA-Z$] [-\w\d$]* '('
        """
        match = re.match(r'^(-*[_a-zA-Z$][-\w\d$]*)\(([ \t]*)', self.s)
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
        match = re.match(r'^([{}])', self.s)
        if match:
            self._skip_number(1)
            brace = match.group(1)
            return Token(brace, brace)

    def paren(self):
        """
        '(' | ')' ' '*
        """
        match = re.match(r'^([()])([ \t]*)', self.s)
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
        match = re.match(r'^#([a-fA-F0-9]{8})[ \t]*', self.s)
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

    def rrggbb(self):
        """
        #rrggbb
        """
        match = re.match(r'^#([a-fA-F0-9]{6})[ \t]*', self.s)
        if match:
            self._skip_string(match.group(0))
            rgb = match.group(1)
            r = int(rgb[0:2], 16)
            g = int(rgb[2:4], 16)
            b = int(rgb[4:6], 16)
            color = RGBA(r, g, b, 1)
            color.raw = match.group(0)
            return Token('color', color)

    def rgba(self):
        """
        #rgba
        """
        match = re.match(r'^#([a-fA-F0-9]{4})[ \t]*', self.s)
        if match:
            self._skip_string(match.group(0))
            rgb = match.group(1)
            r = int(f'{rgb[0]}{rgb[0]}', 16)
            g = int(f'{rgb[1]}{rgb[1]}', 16)
            b = int(f'{rgb[2]}{rgb[2]}', 16)
            a = int(f'{rgb[3]}{rgb[3]}', 16)
            color = RGBA(r, g, b, a/255)
            color.raw = match.group(0)
            return Token('color', color)

    def rgb(self):
        """
        #rgb
        """
        match = re.match(r'^#([a-fA-F0-9]{3})[ \t]*', self.s)
        if match:
            self._skip_string(match.group(0))
            rgb = match.group(1)
            r = int(f'{rgb[0]}{rgb[0]}', 16)
            g = int(f'{rgb[1]}{rgb[1]}', 16)
            b = int(f'{rgb[2]}{rgb[2]}', 16)
            color = RGBA(r, g, b, 1)
            color.raw = match.group(0)
            return Token('color', color)

    def nn(self):
        """
        #nn
        """
        match = re.match(r'^#([a-fA-F0-9]{2})[ \t]*', self.s)
        if match:
            self._skip_string(match.group(0))
            n = int(match.group(1), 16)
            color = RGBA(n, n, n, 1)
            color.raw = match.group(0)
            return Token('color', color)

    def n(self):
        """
        #n
        """
        match = re.match(r'^#([a-fA-F0-9]{1})[ \t]*', self.s)
        if match:
            self._skip_string(match.group(0))
            n = int(f'{match.group(1)}{match.group(1)}', 16)
            color = RGBA(n, n, n, 1)
            color.raw = match.group(0)
            return Token('color', color)

    def color(self):
        tok = self.rrggbbaa()
        if tok:
            return tok
        tok = self.rrggbb()
        if tok:
            return tok
        tok = self.rgba()
        if tok:
            return tok
        tok = self.rgb()
        if tok:
            return tok
        tok = self.nn()
        if tok:
            return tok
        tok = self.n()
        if tok:
            return tok

    def string(self):
        """
        '"' [^"]+ '"' | "'"" [^']+ "'"
        """
        match = re.match(r'^("[^"]*"|\'[^\']*\')[ \t]*', self.s)
        if match:
            self._skip_string(match.group(0))
            string = match.group(0).strip()[1:-1]
            quote = match.group(0)[0]
            return Token('string', String(string, quote))

    def unit(self):
        """
        '-'? (digit+ | digit* '.' digit+) unit
        """
        match = re.match(r'^(-)?(\d+\.\d+|\d+|\.\d+)(%|[a-zA-Z]+)?[ \t]*',
                         self.s)
        if match:
            self._skip_string(match.group(0))
            n = float(match.group(2))
            if match.group(1) == '-':
                n = -n
            unit = Unit(n, match.group(3))
            unit.raw = match.group(0)
            return Token('unit', unit)

    def namedop(self):
        """
        'not' | 'and' | 'or' | 'is' | 'is not' | 'isnt' | 'is a' | 'is defined'
        """
        match = re.match(r'^(not|and|or|is a|is defined|isnt|is not|is)'
                         r'(?!-)\b([ \t]*)', self.s)
        if match:
            self._skip_string(match.group(0))
            op = match.group(1)
            if self.is_part_of_selector():
                tok = Token('ident', Ident(match.group(0)))
            else:
                op = self.alias.get(op, op)
                tok = Token(op, op)
            tok.space = match.group(2)
            return tok

    def boolean(self):
        """
        true | false
        """
        match = re.match(r'^(true|false)\b([ \t]*)', self.s)
        if match:
            self._skip_string(match.group(0))
            val = Boolean('true' == match.group(1))
            tok = Token('boolean', val)
            tok.space = match.group(2)
            return tok

    def unicode(self):
        """
        'U+' [0-9A-Fa-f?]{1,6}(?:-[0-9A-Fa-f]{1,6})?
        """
        match = re.match(r'^u\+[0-9a-f?]{1,6}(?:-[0-9a-f]{1,6})?',
                         self.s,
                         flags=re.IGNORECASE)
        if match:
            self._skip_string(match.group(0))
            return Token('literal', Literal(match.group(0)))

    def ident(self):
        r"""
        -*[_a-zA-Z$] [-\w\d$]*
        """
        match = re.match(r'^-*[_a-zA-Z$][-\w\d$]*', self.s)
        if match:
            self._skip_string(match.group(0))
            return Token('ident', Ident(match.group(0)))

    def _tok_with_location(self, tok, lineno, column):
        tok.lineno = lineno
        tok.column = column
        return tok
