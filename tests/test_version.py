from stilus import __version__
from stilus.__version__ import VERSION


def test_version():
    assert __version__.__version__ == '.'.join(map(str, VERSION))
