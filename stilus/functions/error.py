from stilus.exceptions import StilusError
from stilus.utils import assert_type


def error(msg, evaluator=None):
    assert_type(msg, 'string', 'msg')
    err = StilusError(msg.value)
    err.from_stilus = True
    raise err
