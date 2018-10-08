from stilus.nodes.boolean import Boolean, true, false


def test_is_true():
    assert Boolean(True).is_true()


def test_is_false():
    assert Boolean(False).is_false()


def test_negate():
    boolean = Boolean(True)
    assert boolean.negate().is_false()


def test_string():
    boolean = Boolean(False)
    assert f'{boolean}' == 'false'


def test_true():
    assert true == Boolean(True)


def test_false():
    assert false == Boolean(False)


def test_name():
    boolean = Boolean(False)
    assert boolean.name == 'boolean'
