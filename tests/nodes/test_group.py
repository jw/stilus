from stilus.nodes.block import Block
from stilus.nodes.group import Group
from stilus.nodes.selector import Selector


def test_group():
    group = Group()
    assert group.node_name == "group"
    assert len(group.nodes) == 0
    assert len(group.extends) == 0
    assert f"{group}" == f"{group.nodes}:{group.extends}"


def test_group_add_selector():
    group = Group()
    selector = Selector(["abc", "def"])
    selector.optional = True
    group.append(selector)
    assert len(group.nodes) == 1
    assert group.nodes[0] == selector
    assert group.has_only_placeholders() is False


def test_group_placeholder():
    group = Group()
    selector = Selector(["abc", "def"])
    selector.value = "$foo"
    group.append(selector)
    assert group.has_only_placeholders() is True


def test_group_block():
    group = Group()
    selector = Selector(["abc", "def"])
    selector.value = "$foo"
    group.append(selector)
    assert group.block is None
    block = Block("hello", "there")
    group.block = block
    assert group.block == block
