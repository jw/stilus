from stilus.nodes.ident import Ident


def test_ident():
    ident = Ident('string', 'value', True)
    assert ident.string == 'string'
    assert ident.value == 'value'
    assert ident.mixin is True
    assert ident.name == 'ident'
    assert ident.is_empty() is False


def test_ident_no_value():
    ident = Ident('name', None, True)
    assert ident.name == 'ident'
    assert ident.string == 'name'
    from stilus.nodes.null import null
    assert ident.value == null
    assert ident.mixin is True
    assert ident.is_empty() is True


def test_coerce():
    ident_1 = Ident('first', None, True)
    ident_2 = Ident('second', None, True)
    assert ident_1.coerce(ident_2).string == 'second'
