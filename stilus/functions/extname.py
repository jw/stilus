from pathlib import Path

from utils import assert_string


def extname(p, evaluator=None):
    assert_string(p, 'path')
    return Path(p.value).suffix
