from stilus.nodes.expression import Expression
from stilus.nodes.feature import Feature
from stilus.nodes.ident import Ident


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
    clone = feature.clone()
    assert clone == feature
