from stilus.nodes.root import Root
from stilus.parser import Parser


def test_parser():
    parser = Parser('Hello there', {})
    assert parser.root == Root()
    assert parser.options == {'prefix': '', 'root': Root()}
    assert parser.css == 0
    assert parser.parens == 0
    assert parser.prefix == ''
