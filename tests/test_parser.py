from stilus.nodes.root import Root
from stilus.parser import Parser


def test_parser():
    parser = Parser('abc\n  color: red\n', {})
    assert parser.root == Root()
    assert parser.options == {'prefix': '', 'root': Root()}
    assert parser.css == 0
    assert parser.parens == 0
    assert parser.prefix == ''
    # node = parser.parse()
    # print(node)


def test_parser_root():
    parser = Parser('', {})
    assert parser.parse() == Root()


if __name__ == '__main__':
    test_parser_root()
