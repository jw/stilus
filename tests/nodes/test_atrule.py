from stilus.nodes.atrule import Atrule


def test_atrule():
    atrule = Atrule('media')
    assert atrule.node_name == 'atrule'
    assert atrule.type == 'media'
    assert atrule.segments is None
    assert atrule.block is None


def test_atrule_clone():
    atrule = Atrule('media')
    clone = atrule.clone()
    assert clone == atrule
