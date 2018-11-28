from stilus.nodes.null import Null, null


def test_null():
    assert Null().node_name == 'null'
    assert Null().is_null() is True
    assert hash(Null()) == hash(None)
    from stilus.nodes.boolean import false
    assert Null().to_boolean() == false
    assert Null() == null
