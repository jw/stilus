from stilus.lexer import Lexer


def test_lexer():
    lexer = Lexer('abc\n  def\n  \nklm\n', None)
    tokens = [t for t in lexer]
    print(tokens)
    assert len(tokens) == 7
