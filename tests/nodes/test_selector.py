from stilus.nodes.selector import Selector


def test_selector():
    selector = Selector(['segment1', 'segment2'])
    assert selector.node_name == 'selector'
    assert len(selector.segments) == 2
    assert selector.inherits is True
    assert selector.optional is False
    assert f'{selector}' == f"['segment1', 'segment2']"
    selector.optional = True
    assert f'{selector}' == f"['segment1', 'segment2'] !optional"
    assert selector.is_placeholder() is False


def test_selector_is_placeholder():
    selector = Selector(['segment1', 'segment2'])
    selector.value = 'abc'
    assert selector.is_placeholder() is False
    selector.value = 'ab$'
    assert selector.is_placeholder() is False
    selector.value = '$foo'
    assert selector.is_placeholder() is True
