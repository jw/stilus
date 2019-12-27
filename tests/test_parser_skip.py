from unittest.mock import Mock

from stilus.lexer import Token
from stilus.parser import Parser


def test_parser_skip():
    parser = Parser('abc\n  color: red\n', {})
    parser.skip('ident')
    node = parser.next()
    assert node.type == 'indent'
    assert node.value is None

    parser = Parser('abc\n  color: red\n', {})
    parser.skip(['ident', 'indent'])
    node = parser.next()
    assert node.type == ':'
    assert node.value == ':'


def test_parser_skip_whitespaces():
    parser = Parser('abc\n  color: red\n', {})

    # all whitespace elements
    tokens = [Token('space'), Token('indent'), Token('outdent'),
              Token('newline'), Token('ident')]
    parser.lexer.lookahead = Mock(side_effect=tokens)
    parser.lexer.next = Mock(side_effect=tokens)
    parser.skip_whitespace()
    assert parser.lexer.lookahead.call_count == 5
    assert parser.lexer.next.call_count == 4
    assert parser.next() == Token('ident')

    # smaller
    tokens = [Token('space'), Token('indent'), Token('{')]
    parser.lexer.lookahead = Mock(side_effect=tokens)
    parser.lexer.next = Mock(side_effect=tokens)
    parser.skip_whitespace()
    assert parser.lexer.lookahead.call_count == 3
    assert parser.lexer.next.call_count == 2
    assert parser.next() == Token('{')


def test_parser_skip_spaces():
    parser = Parser('abc\n  color: red\n', {})

    tokens = [Token('space'), Token('space'), Token('outdent')]
    parser.lexer.lookahead = Mock(side_effect=tokens)
    parser.lexer.next = Mock(side_effect=tokens)
    parser.skip_spaces()
    assert parser.lexer.lookahead.call_count == 3
    assert parser.lexer.next.call_count == 2
    assert parser.next() == Token('outdent')


def test_parser_skip_spaces_and_comments():
    parser = Parser('abc\n  color: red\n', {})

    tokens = [Token('space'), Token('comment'), Token('space'),
              Token('comment'), Token('space'), Token('outdent')]
    parser.lexer.lookahead = Mock(side_effect=tokens)
    parser.lexer.next = Mock(side_effect=tokens)
    parser.skip_spaces_and_comments()
    assert parser.lexer.lookahead.call_count == 6
    assert parser.lexer.next.call_count == 5
    assert parser.next() == Token('outdent')
