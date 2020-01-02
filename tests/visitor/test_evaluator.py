from stilus.parser import Parser
from stilus.visitor.evaluator import Evaluator


def test_evaluator_create():
    parser = Parser("abc\n  color: red\n", {})
    root = parser.parse()
    evaluator = Evaluator(root, parser=parser, options={})
    result = evaluator.evaluate()
    assert result.node_name == "root"
    assert result.nodes[0].node_name == "group"
    assert result.nodes[0].nodes[0].node_name == "selector"
    assert result.nodes[0].nodes[0].block.node_name == "block"
    assert result.nodes[0].nodes[0].block.nodes[0].node_name == "property"
    property = result.nodes[0].nodes[0].block.nodes[0]
    assert property.expr.node_name == "expression"
    assert property.expr.nodes[0].r == 255
    assert property.expr.nodes[0].name == "red"
    assert property.expr.nodes[0].a == 1
    assert property.expr.nodes[0].b == 0
    assert property.expr.nodes[0].g == 0
