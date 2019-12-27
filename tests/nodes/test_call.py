from stilus.nodes.call import Call


def test_call():
    call = Call('find_it_all', ['element_1', 'element_2'])
    assert call.args == ['element_1', 'element_2']
    assert call.function_name == 'find_it_all'
