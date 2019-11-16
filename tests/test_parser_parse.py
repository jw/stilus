from nodes.ident import Ident
from nodes.literal import Literal
from nodes.null import null
from parser import Parser


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
    assert property.segments[0] == Ident('color', null, lineno=2, column=3)
    assert len(property.expr.nodes) == 1
    assert property.expr.nodes[0] == Ident('red', null, lineno=2, column=10)
