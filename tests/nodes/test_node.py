import pytest

from stilus.nodes.node import Node, CoercionError


def test_node():
    node = Node(value='value')
    assert node.value == 'value'
    assert node.filename is None
    assert node.lineno == 1
    assert node.column == 1

    node = Node(value='value', filename='filename')
    assert node.value == 'value'
    assert node.filename == 'filename'
    assert node.lineno == 1
    assert node.column == 1

    node = Node(value='value', filename='filename', lineno=10)
    assert node.value == 'value'
    assert node.filename == 'filename'
    assert node.lineno == 10
    assert node.column == 1

    node = Node(value='value', filename='filename', lineno=10, column=42)
    assert node.value == 'value'
    assert node.filename == 'filename'
    assert node.lineno == 10
    assert node.column == 42


def test_hash():
    node = Node()
    assert node.hash() is None
    node = Node(42)
    assert node.hash() == 42


def test_name():
    node = Node()
    assert node.node_name == 'node'


def test_to_boolean():
    node = Node()
    from stilus.nodes.boolean import true
    assert node.to_boolean() is true


def test_first():
    node = Node()
    assert node.first() is node


def test_valid_coerce():
    node_1 = Node()
    node_2 = Node()
    assert node_1.coerce(node_2) == node_2


def test_invalid_coerce():
    from stilus.nodes.null import null
    node_1 = Node()
    node_2 = null
    with pytest.raises(CoercionError) as excinfo:
        node_1.coerce(node_2)
    assert 'cannot coerce null to node' in str(excinfo.value)
