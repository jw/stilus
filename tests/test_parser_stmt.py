from collections import deque
from unittest.mock import MagicMock

from lexer import Token
from nodes.group import Group
from nodes.ident import Ident
from nodes.literal import Literal
from nodes.null import null
from parser import Parser


def test_parser_selector_parts():
    parser = Parser('abc\n  color: red\n', {})
    assert parser.selector_parts() == deque([Literal('abc')])
    parser = Parser('abc def efg\n  color: red\n', {})
    assert parser.selector_parts() == deque([Literal('abc'), Literal(' '),
                                             Literal('def'), Literal(' '),
                                             Literal('efg')])
    parser = Parser('abc:\n  color: red\n', {})
    assert parser.selector_parts() == deque([Literal('abc'), Literal(':'),
                                             Literal('color'), Literal(':'),
                                             Literal(' '), Literal('red')])


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
    assert list.nodes[0] == Ident('color', null, False, lineno=1, column=1)


def test_parser_property():
    parser = Parser('color: red\n', {})
    property = parser.property()
    assert property.segments[0] == Ident('color', null, False,
                                         lineno=1, column=1)
    assert property.expr.nodes[0] == Ident('red', null, False,
                                           lineno=1, column=8)


def test_parser_selector():
    parser = Parser('abc\n  color: red\n', {})
    selector = parser.stmt_selector()
    assert selector.node_name == 'group'
    assert type(selector) == Group
    assert len(selector.nodes) == 1
    assert selector.nodes[0].node_name == 'selector'
    assert len(selector.nodes[0].segments) == 1
    assert selector.nodes[0].segments[0] == Literal('abc')
    block = selector.nodes[0].block
    assert block.node_name == 'block'
    assert len(block.nodes) == 1
    property = block.nodes[0]
    assert property.node_name == 'property'
    assert len(property.segments) == 1
    assert property.segments[0] == Ident('color', null, lineno=2, column=3)
    assert len(property.expr.nodes) == 1
    assert property.expr.nodes[0] == Ident('red', null, lineno=2, column=10)
