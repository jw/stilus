from nodes.expression import Expression
from nodes.feature import Feature
from nodes.ident import Ident


def test_feature():
    foo = Ident('foo')
    bar = Ident('bar')
    feature = Feature([foo, bar])
    assert feature.node_name == 'feature'
    assert feature.segments == [foo, bar]
    assert feature.expr is None
    expression = Expression()
    feature.expr = expression
    assert feature.expr == expression
