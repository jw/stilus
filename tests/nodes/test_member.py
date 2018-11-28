from stilus.nodes.member import Member


def test_member():
    member = Member('left', 'right')
    assert member.node_name == 'member'
    assert member.left == 'left'
    assert member.right == 'right'
    clone = member.clone()
    assert clone == member
