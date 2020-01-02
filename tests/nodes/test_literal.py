from stilus.nodes.literal import Literal


def test_literal():
    literal = Literal("value", True, "prefixed")
    assert literal.value == "value"
    assert literal.string == "value"
    assert literal.css is True
    assert literal.prefixed == "prefixed"
    assert literal.node_name == "literal"
    clone = literal.clone()
    assert clone == literal


def test_coerce():
    literal_1 = Literal("first")
    literal_2 = Literal("second")
    assert literal_1.coerce(literal_2).string == "second"


def test_operate():
    literal_1 = Literal("foo")
    literal_2 = Literal("bar")
    assert literal_1.operate("+", literal_2).string == "foobar"


def test_hash():
    literal = Literal("foo")
    assert literal.hash() == "foo"
