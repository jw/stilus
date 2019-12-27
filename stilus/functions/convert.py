from stilus.utils import assert_string, parse_string


def convert(str, evaluator=None):
    assert_string(str, 'string')
    return parse_string(str.string)
