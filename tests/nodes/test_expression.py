import pytest
from exceptions import StilusError

from nodes.boolean import Boolean
from nodes.expression import Expression
from nodes.ident import Ident


def test_empty_expression():
    from nodes.null import null
    from nodes.boolean import false
    expression = Expression()
    assert len(expression) == 0
    assert expression.is_empty()
    assert expression.first() is null
    assert expression.to_boolean() is false


def test_expression_creation():
    expression = Expression()
    assert not expression.is_list
    assert not expression.preserve
    assert expression.node_name == 'expression'


def test_expression_creation_with_is_list_and_preserve():
    expression = Expression(is_list=True, preserve=True)
    assert expression.is_list
    assert expression.preserve


def test_expression_make_is_list_and_preserve():
    expression = Expression()
    expression.is_list = True
    expression.preserve = True
    assert expression.is_list
    assert expression.preserve


def test_expression_append():
    from nodes.null import null
    from nodes.boolean import true
    from nodes.boolean import false
    expression = Expression()
    expression.append(null)
    expression.append(true)
    expression.append(false)
    assert len(expression) == 3


def test_expression_string_first_boolean():
    from nodes.boolean import true
    from nodes.boolean import false
    from nodes.null import null
    expression = Expression()
    expression.append(true)
    expression.append(false)
    expression.append(null)
    assert str(expression) == '(true false null)'
    expression.is_list = True
    assert str(expression) == '(true, false, null)'
    assert expression.first() is true
    assert expression.to_boolean() is true


def test_expression_operate_in():
    # empty expression
    expression = Expression()
    other_expression = Expression()
    other_expression.append(Ident('foo'))
    other_expression.append(Ident('bar'))
    assert expression.operate('in', other_expression) == Boolean(False)
    with pytest.raises(StilusError):
        other_expression.operate('in', expression) == Boolean(True)

    # same expression
    expression = Expression()
    expression.append(Ident('foo'))
    expression.append(Ident('bar'))
    assert expression.operate('in', expression) == Boolean(False)

    # other expression
    expression = Expression()
    expression.append(Ident('foo'))
    expression.append(Ident('bar'))
    other_expression = Expression()
    other_expression.append(Ident('bar'))
    assert other_expression.operate('in', expression) == Boolean(True)


def test_expression_hash():
    expression = Expression()
    assert expression.hash() == ''
    expression = Expression()
    expression.append(Ident('foo'))
    assert expression.hash() == 'foo'
    other_expression = Expression()
    other_expression.append(Ident('foo'))
    other_expression.append(Ident('bar'))
    assert other_expression.hash() == 'foo::bar'
    from nodes.null import null
    from nodes.boolean import true
    from nodes.boolean import false
    expression = Expression()
    expression.append(null)
    expression.append(true)
    expression.append(false)
    # in stylus null::true::false is returned; stilus returns the Python types
    assert expression.hash() == 'None::True::False'
