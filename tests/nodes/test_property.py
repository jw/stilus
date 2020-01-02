from stilus.nodes.expression import Expression
from stilus.nodes.ident import Ident
from stilus.nodes.property import Property


def test_property():
    property = Property(["foo", "bar"])
    assert property.node_name == "property"
    assert len(property.segments) == 2
    assert property.expr is None
    assert f"{property}" == "property(foobar, None)"


def test_property_expression():
    from stilus.nodes.boolean import true
    from stilus.nodes.boolean import false
    from stilus.nodes.null import null

    expression = Expression()
    expression.append(true)
    expression.append(false)
    expression.append(null)
    property = Property(["foo", "bar"], expression)
    assert property.node_name == "property"
    assert len(property.segments) == 2
    assert property.expr is expression
    assert f"{property}" == "property(foobar, (true false null))"
    expression.is_list = True
    assert f"{property}" == "property(foobar, (true, false, null))"


def test_property_color_red():
    # color: red
    expression = Expression()
    expression.append(Ident("red"))
    property = Property(["color"], expression)
    assert property.expr == expression
    assert len(property.segments) == 1
    assert f"{property}" == "property(color, (red))"
