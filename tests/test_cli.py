from click.testing import CliRunner
from stilus import bootstrap, __version__


def test_cli():
    runner = CliRunner()
    result = runner.invoke(bootstrap.cli, ['--version'])
    assert result.exit_code == 0
    assert result.output == __version__ + '\n'
