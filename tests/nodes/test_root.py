from nodes.boolean import true, false
from nodes.null import null
from nodes.root import Root


def test_root():
    root = Root()
    assert root.node_name == 'root'
    root.append(null)
    assert root.nodes == [null]
    root.unshift(true)
    assert root.nodes == [true, null]
    root.unshift(false)
    assert root.nodes == [false, true, null]
    root.append(false)
    assert root.nodes == [false, true, null, false]
