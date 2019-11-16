from pathlib import Path

from utils import assert_string


def dirname(p, evaluator=None):
    assert_string(p, 'path')
    return str(Path(p).parent)
