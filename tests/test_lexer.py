from collections import deque

from stilus.lexer import Lexer, Token
from stilus.nodes.boolean import true
from stilus.nodes.color import RGBA
from stilus.nodes.ident import Ident
from stilus.nodes.literal import Literal
from stilus.nodes.string import String
from stilus.nodes.unit import Unit


def test_lexer_token():
    left = Token('selector', 'abc: def')
    right = Token('selector', 'abc: def')
    assert left == right
    assert left.anonymous is False
    assert left.space is None
    right.space = 10
    assert left != right


def test_lexer_token_string():
    token = Token('indent', 'abc: def')
    assert str(token) == 'Token(indent, abc: def)'
    token.space = 5
    assert str(token) == 'Token(indent, abc: def, space=5)'
    token = Token('eos')
    assert str(token) == 'Token(eos, None)'


def test_lexer_empty_string():
    lexer = Lexer('Hello there!', {})
    assert lexer.stash == deque([])
    assert lexer.indent_stack == deque([])
    assert lexer.indent_re is None
    assert lexer.lineno == 1
    assert lexer.column == 1
    assert lexer.options == {}
    assert lexer.prev is None
    assert lexer.is_url is False
    assert lexer.at_eos is False


def test_lexer_eq():
    left = Lexer('foobar', {'fizz': 'fuzz'})
    right = Lexer('foobar', {'fizz': 'fuzz'})
    assert left == right
    wrong = Lexer('fizz', {})
    assert left != wrong


def test_lexer_clean():
    lexer = Lexer('Hello', {})
    assert lexer.clean('hello') == 'hello'
    assert lexer.clean('\uFEFFhello') == 'hello'
    # empty
    lexer = Lexer('', {})
    assert lexer.s == ''
    assert lexer.advance() == Token('eos')
    # empty lines
    lexer = Lexer('\n\n\n', {})
    assert lexer.s == '\n'
    assert lexer.advance() == Token('newline')
    assert lexer.advance() == Token('eos')
    # our most basic example
    lexer = Lexer('abc:\n  color: black\n', {})
    assert lexer.s == 'abc:\rcolor: black\n'
    # weird stuff at the beginning and the end
    lexer = Lexer('\t\t\nabc;;;\n\t\n', {})
    assert lexer.s == '\t\t\nabc;;;\n'
    # whitespaces (and newlines) at the end must be removed
    lexer = Lexer('abc\t\n\t\f', {})
    assert lexer.s == 'abc\n'
    # \r\n to \n
    lexer = Lexer('abc\r\ndef\n\n', {})
    assert lexer.s == 'abc\ndef\n'
    lexer = Lexer('abc\r\n\r\ndef\n\n', {})
    assert lexer.s == 'abc\n\ndef\n'
    # \ * string to \r
    lexer = Lexer('abc\n   \\    \ndef\n', {})
    assert lexer.s == 'abc\n   \rdef\n'
    lexer = Lexer('abc\n   \\    \n\\  \ndef\n', {})
    assert lexer.s == 'abc\n   \r\rdef\n'
    # comments
    lexer = Lexer('abc: // some comment\n  color: #FFF\n', {})
    assert lexer.s == 'abc:\rcolor: #FFF\n'
    lexer = Lexer('abc: /* some comment\n * longer one\n * ends now */\n', {})
    assert lexer.s == 'abc: /* some comment\n * longer one\n * ends now */\n'
    lexer = Lexer('abc: /*! some comment\n * longer one\n * ends now */\n', {})
    assert lexer.s == 'abc: /*! some comment\n * longer one\n * ends now */\n'
    # more comments
    lexer = Lexer('abc(// another comment\ndef ,// yet another comment\n', {})
    assert lexer.s == 'abc(\rdef ,\r'
    # whitespace, \n and ) or ,
    lexer = Lexer('abc: \t\f\t\n  )def\n', {})
    assert lexer.s == 'abc:)\rdef\n'
    lexer = Lexer('abc: \t\f\t\n  ,def\n', {})
    assert lexer.s == 'abc:,\rdef\n'


def test_lexer_is_part_of_selector():
    lexer = Lexer('^if.null,[bar],abc  color: black\n', {})
    assert lexer.next() == Token('selector', '^')
    assert lexer.next() == Token('if', 'if')
    assert lexer.next() == Token('.', '.', '')
    assert lexer.next() == Token('ident', Ident('null'))
    lexer = Lexer('^#fif: black\n', {})
    assert lexer.next() == Token('selector', '^')
    assert lexer.next() == Token('color', RGBA(255, 255, 255, 1))
    assert lexer.next() == Token('ident', Ident('if'))


def test_lexer_next():
    lexer = Lexer('abc:\n  color: #11223311\n', {})
    assert lexer.next() == Token('ident', Ident('abc', 'abc'))
    assert lexer.next() == Token(':', ':', '')


def test_lexer_peek():
    lexer = Lexer('abc:\n  color: #11223311\n', {})
    abc = Token('ident', Ident('abc', 'abc'))
    assert lexer.peek() == abc
    assert lexer.peek() == abc
    assert lexer.next() == abc
    colon = Token(':', ':', '')
    assert lexer.peek() == Token(':', ':', '')
    assert lexer.next() == colon


def test_lexer_indent_outdent():
    lexer = Lexer('abc, def:\n'
                  '  color: #12345678\n'
                  '    foo: null\n', {})
    tokens = [token for token in lexer]
    assert tokens[7] == Token('indent')
    assert tokens[11] == Token('outdent')


def test_lexer_ident_colon_null_newline_eos():
    lexer = Lexer('abc:\n  color: null\n', {})
    tokens = [token for token in lexer]
    assert tokens[0] == Token('ident', Ident('abc', 'abc'))
    assert tokens[1] == Token(':', ':', '')
    assert tokens[2] == Token('ident', Ident('color', 'color'))
    assert tokens[3] == Token(':', ':', ' ')
    assert tokens[4] == Token('null')
    assert tokens[5] == Token('newline')
    assert tokens[6] == Token('eos')


def test_lexer_ident_colon_colors():
    lexer = Lexer('abc: #11223311, #aabbcc, #abc1, #fff, #dd, #e', {})
    tokens = [token for token in lexer]
    assert tokens[0] == Token('ident', Ident('abc', 'abc'))
    assert tokens[1] == Token(':', ':', ' ')
    assert tokens[2] == Token('color', RGBA(17, 34, 51, 0.67))
    assert tokens[4] == Token('color', RGBA(170, 187, 204, 1))
    assert tokens[6] == Token('color', RGBA(170, 187, 204, 0.067))
    assert tokens[8] == Token('color', RGBA(255, 255, 255, 1))
    assert tokens[10] == Token('color', RGBA(221, 221, 221, 1))
    assert tokens[12] == Token('color', RGBA(238, 238, 238, 1))


def test_lexer_ident_space():
    lexer = Lexer('abc def klm:\n  xyz abc\n', {})
    tokens = [token for token in lexer]
    assert tokens[0] == Token('ident', Ident('abc', 'abc'))
    assert tokens[1] == Token('space')
    assert tokens[2] == Token('ident', Ident('def', 'def'))
    assert tokens[3] == Token('space')
    assert tokens[4] == Token('ident', Ident('klm', 'klm'))


def test_lexer_function_paren_braces_sep_unit():
    lexer = Lexer('bg()\n'
                  '  background: blue\n'
                  '\n'
                  'body {\n'
                  '  bg(); width: 100px\n'
                  '}\n',
                  {})
    tokens = [token for token in lexer]
    assert tokens[0] == Token('function', Ident('bg', Ident('null')), '')
    assert tokens[1] == Token(')', ')', '')
    assert tokens[9] == Token('{', '{')
    assert tokens[11] == Token('function', Ident('bg', Ident('null')), '')
    assert tokens[13] == Token(';', None)
    assert tokens[16] == Token('unit', Unit(100.0, 'px'))
    assert tokens[18] == Token('}', '}')


def test_lexer_keyword_string():
    lexer = Lexer('if "fizz":\n  return foo;\n', {})
    tokens = [token for token in lexer]
    assert tokens[0] == Token('if', 'if')
    assert tokens[1] == Token('string', String('fizz', '"'))
    assert tokens[3] == Token('return', 'return')


def test_lexer_boolean_unicode():
    lexer = Lexer('if true:\n  return U+abcdef;\n', {})
    tokens = [token for token in lexer]
    assert tokens[1] == Token('boolean', true, '')
    assert tokens[4] == Token('literal', Literal('U+abcdef'))


def test_lexer_functions():
    lexer = Lexer('mixin(add) {\n'
                  '  mul = @(c, d) {\n'
                  '    c * d\n'
                  '  }\n'
                  '  width: add(2, 3) + mul(4, 5)\n'
                  '}\n',
                  {})
    tokens = [token for token in lexer]
    assert tokens[0] == Token('function', Ident('mixin', Ident('null')), '')
    anon_fun_token = Token('function', Ident('anonymous'))
    anon_fun_token.anonymous = True
    assert tokens[8] == anon_fun_token


def test_lexer_atrules():
    lexer = Lexer('@viewport {\n'
                  '  color: blue\n'
                  '}\n'
                  '\n'
                  '@namespace svg "http://www.w3.org/2000/svg"\n'
                  '@-moz-viewport\n',
                  {})
    tokens = [token for token in lexer]
    assert tokens[0] == Token('atrule', 'viewport')
    assert tokens[9] == Token('namespace')
    assert tokens[12] == Token('string',
                               String('http://www.w3.org/2000/svg', '"'))
    assert tokens[14] == Token('atrule', '-moz-viewport')


def test_lexer_namedop():
    lexer = Lexer('foo is a bar\nfizz isnt a fuzz\n', {})
    tokens = [token for token in lexer]
    assert tokens[2] == Token('is a', 'is a', ' ')
    assert tokens[7] == Token('!=', '!=', ' ')


def test_lexer_urlchars_important():
    lexer = Lexer('url("/images/foo.png")\n'
                  '!important foo', {})
    tokens = [token for token in lexer]
    assert tokens[1] == Token('string', String('/images/foo.png', '"'))
    assert tokens[4] == Token('ident', Ident('!important', '!important'))


def test_lexer_escaped():
    lexer = Lexer('bar: 1 \\+ 2\n', {})
    tokens = [token for token in lexer]
    assert tokens[3] == Token('ident', Literal('+'))
