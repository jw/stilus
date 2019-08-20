import pytest

from stilus.exceptions import ParseError
from stilus.nodes.ident import Ident
from stilus.parser import Parser


def test_parser_construct():
    parser = Parser('abc\n  color: red\n', {})
    assert parser.css == 0
    assert parser.parens == 0
    assert parser.prefix == ''


def test_parser_accept():
    parser = Parser('abc\n  color: red\n', {})
    assert parser.accept(':') is None  # invalid
    assert parser.accept('ident').type == 'ident'  # abc
    assert parser.accept('indent').type == 'indent'
    assert parser.accept('ident').type == 'ident'  # color
    assert parser.accept(':').type == ':'
    assert parser.accept('ident').type == 'ident'  # red
    assert parser.accept('outdent').type == 'outdent'
    assert parser.accept('eos').type == 'eos'


def test_parser_expect():
    parser = Parser('abc\n  color: red\n', {})
    assert parser.expect('ident').type == 'ident'  # abc
    assert parser.expect('indent').type == 'indent'
    assert parser.expect('ident').type == 'ident'  # color
    assert parser.expect(':').type == ':'
    assert parser.expect('ident').type == 'ident'  # red
    assert parser.expect('outdent').type == 'outdent'
    with pytest.raises(ParseError) as excinfo:
        parser.expect(':') is None  # invalid
    assert 'expected ":", got "eos"' in str(excinfo.value)
    assert parser.expect('eos').type == 'eos'


def test_parser_peek_lookahead_and_next():
    parser = Parser('abc\n  color: red\n', {})

    # next
    node = parser.next()
    assert node.type == 'ident'
    assert node.value == Ident('abc', lineno=1, column=1)
    node = parser.next()
    assert node.type == 'indent'
    assert node.value is None

    # peek
    assert parser.peek().type == 'ident'
    assert parser.peek().type == 'ident'
    assert parser.peek().type == 'ident'

    # lookahead
    assert parser.lookahead(1) == parser.peek()
    assert parser.lookahead(2).type == ':'
    assert parser.lookahead(2).value == ':'
    assert parser.lookahead(2).space == ' '

    # next
    parser.next()
    node = parser.next()
    assert node.type == ':'
    assert node.value == ':'
    assert node.space == ' '

    # combo
    assert parser.peek().type == 'ident'
    parser.next()
    assert parser.peek().type == 'outdent'
    parser.next()
    assert parser.peek().type == 'eos'


def test_parser_iterator():
    parser = Parser('abc\n  color: red\n', {})
    tokens = [token for token in parser]
    assert len(tokens) == 6
    assert tokens[3].type == ':'
    parser = Parser('abc\n  color red\n', {})
    tokens = [token for token in parser]
    assert len(tokens) == 6
    assert tokens[3].type == 'space'
