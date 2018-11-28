from stilus.nodes.iff import Iff


# TODO: implement complete test
def test_property():
    iff = Iff('condition')
    assert iff.node_name == 'iff'
