from nodes.keyframes import Keyframes


def test_keyframes():
    keyframes = Keyframes(['segment1', 'segment2'])
    assert keyframes.prefix == 'official'
    assert keyframes.segments == ['segment1', 'segment2']
    assert keyframes.node_name == 'keyframes'


def test_str():
    keyframes = Keyframes(['segment1', 'segment2'], prefix='foo')
    assert keyframes.prefix == 'foo'
    assert f'{keyframes}' == '@keyframes segment1segment2'
