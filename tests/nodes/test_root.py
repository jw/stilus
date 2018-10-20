from collections import deque

from stilus.nodes.boolean import true, false
from stilus.nodes.null import null
from stilus.nodes.root import Root


def test_root():
    root = Root()
    assert root.name == 'root'
    assert hash(root) == hash(Root())
    root.push(null)
    assert root.nodes == deque([null])
    root.unshift(true)
    assert root.nodes == deque([true, null])
    root.unshift(false)
    assert root.nodes == deque([false, true, null])
    root.push(false)
    assert root.nodes == deque([false, true, null, false])
