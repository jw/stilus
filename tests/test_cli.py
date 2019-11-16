from click.testing import CliRunner

import __version__
import cli


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli.stilus, ['--version'])
    assert result.exit_code == 0
    assert result.output == __version__.__version__ + '\n'


def test_cli_plain():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('foo.styl', 'w') as f:
            f.write('foo\n  abc blue\n')
        result = runner.invoke(cli.stilus, ['foo.styl'])
        assert result.exit_code == 0
        assert result.output == 'foo {\n  abc: #00f;\n}\n'


def test_cli_plain_compress():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('foo.styl', 'w') as f:
            f.write('foo\n  abc blue\n')
        result = runner.invoke(cli.stilus, ['-c', 'foo.styl'])
        assert result.exit_code == 0
        assert result.output == 'foo{abc:#00f}'


def test_cli_stdin():
    runner = CliRunner()
    result = runner.invoke(cli.stilus, input='foo\n  abc red\n')
    assert result.exit_code == 0
    assert result.output == 'foo {\n  abc: #f00;\n}\n'


def test_cli_stdin_compress():
    runner = CliRunner()
    result = runner.invoke(cli.stilus, ['-c'], input='foo\n  abc def\n')
    assert result.exit_code == 0
    assert result.output == 'foo{abc:def}'
