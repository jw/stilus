from stilus.nodes.expression import Expression
from stilus.nodes.property import Property


def test_property():
    property = Property(['foo', 'bar'])
    assert property.name == 'property'
    assert len(property.segments) == 2
    assert property.expr is None
    assert f'{property}' == 'property(foobar, None)'


def test_property_expression():
    from stilus.nodes.boolean import true
    from stilus.nodes.boolean import false
    from stilus.nodes.null import null
    expression = Expression()
    expression.push(true)
    expression.push(false)
    expression.push(null)
    property = Property(['foo', 'bar'], expression)
    assert property.name == 'property'
    assert len(property.segments) == 2
    assert property.expr is expression
    assert f'{property}' == 'property(foobar, (true false null))'
