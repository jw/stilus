from stilus.lexer import Lexer


def test_lexer_empty_string():
    lexer = Lexer('', None)
    tokens = [t for t in lexer]
    assert len(tokens) == 1
