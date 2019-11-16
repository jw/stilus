from nodes.ident import Ident
from nodes.null import null
from nodes.string import String
from nodes.expression import Expression
from nodes.boolean import false, true
from nodes.boolean import Boolean


def test_string():
    assert String('hello', 'there').node_name == 'string'
    assert str(String('hello', null)) == '\'hello\''
    assert str(String('hello', 'there')) == 'therehellothere'
    assert str(String('hello')) == '\'hello\''
    assert String('hello').to_boolean() == true
    assert String('z').to_boolean() == Boolean(True)
    assert String('').to_boolean() == false


def test_coerce():
    first = String('hello')
    other = String('there')
    assert first.coerce(other) == other
    expression = Expression()
    expression.append(String('one'))
    expression.append(String('two'))
    expression.append(String('three'))
    assert first.coerce(expression) == String('one two three')
    assert first.coerce(null) == String('null')
    assert first.coerce(Ident('foobar')) == String('foobar')
