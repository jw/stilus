from nodes.ifnode import If


# TODO: implement complete test
def test_property():
    iff = If('condition')
    assert iff.node_name == 'if'
