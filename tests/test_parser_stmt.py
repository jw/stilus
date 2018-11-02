from unittest.mock import MagicMock

from stilus.lexer import Lexer, Token
from stilus.parser import Parser


def test_parser_is_selector_token():
    pass


def test_parser_line_contains():
    parser = Parser('abc\n  color: red\n', {})
    tokens = [Token('space'), Token('indent'), Token('comments')]
    parser.lexer.lookahead = MagicMock(side_effect=tokens)
    assert parser.line_contains('{') is False
    tokens = [Token('space'), Token('{'), Token('outdent')]
    parser.lexer.lookahead = MagicMock(side_effect=tokens)
    assert parser.line_contains('{') is True


if __name__ == '__main__':

    lexer = Lexer('abc\n  color: red\n', {})
    for token in lexer:
        print(token)
    parser = Parser('abc\n  color: red\n', {})
    parser.next.side_effect
