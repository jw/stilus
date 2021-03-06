from stilus import utils
from stilus.nodes.boolean import true
from stilus.nodes.expression import Expression
from stilus.nodes.unit import Unit


def test_unwrap():
    inner_expression = Expression()
    inner_expression.append(Unit(10))
    inner_expression.append(Unit(20))
    assert utils.unwrap(inner_expression) == inner_expression
    outer_expression = Expression()
    outer_expression.append(inner_expression)
    assert utils.unwrap(outer_expression) == inner_expression


def test_unwrap_double():
    first_expression = Expression()
    first_expression.append(Unit(10))
    first_expression.append(Unit(20))
    inner_expression = Expression()
    inner_expression.append(first_expression)
    outer_expression = Expression()
    outer_expression.append(inner_expression)
    last_expression = Expression()
    last_expression.append(outer_expression)
    assert utils.unwrap(last_expression) == first_expression


def test_unwrap_preserve():
    inner_expression = Expression()
    inner_expression.append(Unit(10))
    inner_expression.append(Unit(20))
    assert utils.unwrap(inner_expression) == inner_expression
    outer_expression = Expression()
    outer_expression.preserve = True
    outer_expression.append(inner_expression)
    assert utils.unwrap(outer_expression) == outer_expression


def test_unwrap_one_than_one():
    inner_expression = Expression()
    inner_expression.append(Unit(10))
    inner_expression.append(Unit(20))
    assert utils.unwrap(inner_expression) == inner_expression
    outer_expression = Expression()
    outer_expression.append(inner_expression)
    outer_expression.append(true)
    assert utils.unwrap(outer_expression) == outer_expression


def test_unwrap_no_expression():
    assert utils.unwrap(true) == true
    assert utils.unwrap(Unit(50, "mm")) == Unit(50, "mm")


def test_compile_selectors():
    # todo: implement me!
    pass
