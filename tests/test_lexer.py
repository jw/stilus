from collections import deque

from stilus.lexer import Lexer, Token
from stilus.nodes.color import RGBA
from stilus.nodes.ident import Ident


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


def test_lexer_next():
    lexer = Lexer('abc:\n  color: #11223311\n', {})
    assert lexer.next() == Token('ident', Ident('abc', 'abc'))
    assert lexer.next() == Token(':', ':', '')


def test_lexer_peek():
    lexer = Lexer('abc:\n  color: #11223311\n', {})
    assert lexer.peek() == Token('ident', Ident('abc', 'abc'))
    assert lexer.peek() == Token('ident', Ident('abc', 'abc'))
    lexer.next()
    assert lexer.peek() == Token(':', ':', '')


def test_lexer_rrggbbaa():
    lexer = Lexer('abc:\n  color: #11223311\n', {})
    assert lexer.advance() == Token('ident', Ident('abc', 'abc'))
    assert lexer.advance() == Token(':', ':', '')
    assert lexer.advance() == Token('ident', Ident('color', 'color'))
    assert lexer.advance() == Token(':', ':', ' ')
    assert lexer.advance() == Token('color', RGBA(17, 34, 51, 0.067))
    assert lexer.advance() == Token('newline')
    assert lexer.advance() == Token('eos')


def test_lexer_ident_space():
    lexer = Lexer('abc def klm:\n  xyz abc\n', {})
    assert lexer.advance() == Token('ident', Ident('abc', 'abc'))
    assert lexer.advance() == Token('space')
    assert lexer.advance() == Token('ident', Ident('def', 'def'))
    assert lexer.advance() == Token('space')
    assert lexer.advance() == Token('ident', Ident('klm', 'klm'))
    assert lexer.advance() == Token(':', ':', '')
