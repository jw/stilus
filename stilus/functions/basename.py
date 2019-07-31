from pathlib import Path

from stilus.utils import assert_string


def basename(p, ext=None, evaluator=None):
    assert_string(p, 'path')
    result = Path(p).name
    if ext and result.endswith(ext.name):
        result[:len(ext.name)]
    return result
