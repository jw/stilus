from click.testing import CliRunner
from stilus import cli, __version__


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli.stilus, ['--version'])
    assert result.exit_code == 0
    assert result.output == __version__ + '\n'
