from nodes.unit import Unit


def test_unit():
    unit = Unit(1000, 'mm')
    assert unit.value == 1000
    assert unit.type == 'mm'
    assert unit.node_name == 'unit'


def test_boolean():
    unit = Unit(1, 'Hz')
    from nodes.boolean import true
    assert unit.to_boolean() == true
    unit = Unit(10)
    from nodes.boolean import Boolean
    assert unit.to_boolean() == Boolean(10)


def test_string():
    assert str(Unit(1, 'Hz')) == '1Hz'
    assert str(Unit(100)) == '100'
