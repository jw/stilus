from stilus.nodes.function import Function


def test_function():
    function = Function('find_it_all', ['element_1', 'element_2'], 'body')
    assert function.node_name == 'function'
    assert function.params == ['element_1', 'element_2']
    assert function.block == 'body'
    assert function.function_name == 'find_it_all'
    assert function.builtin is False


def test_hash():
    function = Function('find_it_all', ['element_1', 'element_2'], 'body')
    assert function.hash() == 'function find_it_all'
