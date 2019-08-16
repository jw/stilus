from stilus.nodes.boolean import true, false
from stilus.nodes.null import null
from stilus.nodes.root import Root


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
