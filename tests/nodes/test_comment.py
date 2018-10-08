from stilus.nodes.comment import Comment


def test_comment():
    comment = Comment('value', True, False)
    assert comment.value == 'value'
    assert comment.suppress is True
    assert comment.inline is False
