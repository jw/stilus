from collections import deque
from unittest.mock import MagicMock

from stilus.lexer import Token
from stilus.nodes.ident import Ident
from stilus.nodes.literal import Literal
from stilus.nodes.null import null
from stilus.parser import Parser


def test_parser_selector_parts():
    parser = Parser('abc\n  color: red\n', {})
    assert parser.selector_parts() == deque([Literal('abc')])
    parser = Parser('abc def efg\n  color: red\n', {})
    assert parser.selector_parts() == deque([Literal('abc'), Literal(' '),
                                             Literal('def'), Literal(' '),
                                             Literal('efg')])


def test_parser_selector_token():
    parser = Parser('', {})
    tokens = [Token('ident'), Token(':')]
    parser.lexer.lookahead = MagicMock(side_effect=tokens)
    parser.lexer.next = MagicMock(side_effect=tokens)
    assert parser.selector_token() == Token('ident')


def test_parser_is_selector_token():
    parser = Parser('', {})
    tokens = [Token('atrule'), Token('ident'), Token('comment'), Token('not')]
    parser.lexer.lookahead = MagicMock(side_effect=tokens)
    assert parser.is_selector_token(1) is False
    assert parser.is_selector_token(2) is True
    assert parser.is_selector_token(3) is True
    assert parser.is_selector_token(4) is False


def test_parser_line_contains():
    parser = Parser('', {})
    tokens = [Token('space'), Token('indent'), Token('comments')]
    parser.lexer.lookahead = MagicMock(side_effect=tokens)
    assert parser.line_contains('{') is False
    tokens = [Token('space'), Token('{'), Token('outdent')]
    parser.lexer.lookahead = MagicMock(side_effect=tokens)
    assert parser.line_contains('{') is True


def test_parser_list():
    parser = Parser('color: red\n', {})
    list = parser.list()
    assert len(list) == 1
    assert list.nodes[0] == Ident('color', null, False)


def test_parser_property():
    parser = Parser('color: red\n', {})
    property = parser.property()
    assert property.segments[0] == Ident('color', null, False)
    assert property.expr.nodes[0] == Ident('red', null, False)