from stilus.utils import assert_string, assert_type


def remove(object, key, evaluator=None):
    assert_type(object, 'objectnode', 'object')
    assert_string(key, 'key')
    if object.has(key.string):
        del object.values[key.string]
    return object
