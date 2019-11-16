from nodes.arguments import Arguments
from nodes.boolean import true
from nodes.expression import Expression
from nodes.unit import Unit


def test_arguments():
    arguments = Arguments()
    assert arguments.node_name == 'arguments'
    assert len(arguments.map) == 0


def test_from_expression():
    expression = Expression()
    expression.append(Unit(10, 'mm'))
    expression.append(true)
    expression.lineno = 42
    expression.column = 13
    expression.is_list = True
    arguments = Arguments.from_expression(expression)
    assert arguments.nodes == expression.nodes
    assert arguments.lineno == expression.lineno
    assert arguments.column == expression.column
    assert arguments.is_list == expression.is_list
