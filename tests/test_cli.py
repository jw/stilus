from click.testing import CliRunner
from stilus import cli, __version__


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli.stilus, ['--version'])
    assert result.exit_code == 0
    assert result.output == __version__ + '\n'


def test_cli_plain():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('foo.styl', 'w') as f:
            f.write('foo\n  abc def\n')
        result = runner.invoke(cli.stilus, ['foo.styl'])
        assert result.exit_code == 0
        assert result.output == 'foo {\n  abc: def;\n}\n\n'


def test_cli_plain_compress():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('foo.styl', 'w') as f:
            f.write('foo\n  abc def\n')
        result = runner.invoke(cli.stilus, ['-c', 'foo.styl'])
        assert result.exit_code == 0
        assert result.output == 'foo{abc:def}'
