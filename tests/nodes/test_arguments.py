from stilus.nodes.arguments import Arguments
from stilus.nodes.boolean import true
from stilus.nodes.expression import Expression
from stilus.nodes.unit import Unit


def test_arguments():
    arguments = Arguments()
    assert arguments.name == 'arguments'
    assert len(arguments.map) == 0


def test_from_expression():
    expression = Expression()
    expression.push(Unit(10, 'mm'))
    expression.push(true)
    expression.lineno = 42
    expression.column = 13
    expression.is_list = True
    arguments = Arguments.from_expression(expression)
    assert arguments.nodes == expression.nodes
    assert arguments.lineno == expression.lineno
    assert arguments.column == expression.column
    assert arguments.is_list == expression.is_list
