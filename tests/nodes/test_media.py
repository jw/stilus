from nodes.media import Media


def test_property():
    media = Media('fizz')
    assert media.node_name == 'media'
    assert media.value == 'fizz'
    assert f'{media}' == '@media fizz'
