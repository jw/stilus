from stilus.nodes.function import Function


def test_function():
    function = Function('find_it_all', ['element_1', 'element_2'], 'body')
    assert function.node_name == 'function'
    assert function.params == ['element_1', 'element_2']
    assert function.body == 'body'
    assert function.fn == ['element_1', 'element_2']
    assert function.function_name == 'find_it_all'
    clone = function.clone()
    assert clone == function


def test_hash():
    function = Function('find_it_all', ['element_1', 'element_2'], 'body')
    assert function.hash() == 'function find_it_all'
