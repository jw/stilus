from pathlib import Path

from stilus.utils import assert_string


def dirname(p, evaluator=None):
    assert_string(p, 'path')
    return str(Path(p).parent)
