from stilus.nodes.ident import Ident
from stilus.nodes.literal import Literal
from stilus.nodes.null import null
from stilus.parser import Parser


def test_parser_parse_basic():
    parser = Parser('abc\n  color: red\n', {})
    root = parser.parse()
    assert root.node_name == 'root'
    assert root.nodes[0].node_name == 'group'
    selector = root.nodes[0].nodes[0]
    assert selector.segments[0] == Literal('abc')
    assert selector.block.parent == root
    assert selector.block.node.node_name == 'group'
    property = selector.block.nodes[0]
    assert property.node_name == 'property'
    assert len(property.segments) == 1
    assert property.segments[0] == Ident('color', null)
    assert len(property.expr.nodes) == 1
    assert property.expr.nodes[0] == Ident('red', null)


if __name__ == '__main__':
    source = '\nsize = 12px\n\nbody\n  font-size size\n\n'
    source = 'body\n  color red\n\n'
    parser = Parser(source, {})
    block = parser.parse()
    print(f'block: {block}')
