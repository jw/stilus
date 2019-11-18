from pathlib import Path

from click.testing import CliRunner

import __version__
import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli.stilus, ['--help'])
    assert result.exit_code == 0
    assert 'Usage: stilus [OPTIONS] [INPUT] [OUTPUT]' in result.output
    assert '-h, --help' in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli.stilus, ['--version'])
    assert result.exit_code == 0
    assert result.output == f'{__version__.__version__}\n'


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


def test_cli_stdin_stdout():
    runner = CliRunner()
    result = runner.invoke(cli.stilus, input='foo\n  abc red\n')
    assert result.exit_code == 0
    assert result.output == 'foo {\n  abc: #f00;\n}\n'


def test_cli_stdin_stdout_compress():
    runner = CliRunner()
    result = runner.invoke(cli.stilus, ['-c'], input='foo\n  abc def\n')
    assert result.exit_code == 0
    assert result.output == 'foo{abc:def}'


def test_cli_out_and_print():
    runner = CliRunner()
    with runner.isolated_filesystem() as fs:
        with open('foo.styl', 'w') as f:
            f.write('foo\n  abc blue\n')
        Path.mkdir(Path('some_directory'))
        result = runner.invoke(cli.stilus,
                               ['--out', 'some_directory', 'foo.styl'])
        css = 'foo {\n  abc: #00f;\n}\n'
        css_file = Path(fs) / Path('some_directory') / Path('foo.css')
        assert css_file.exists() is False
        assert result.exit_code == 0
        assert result.output == css
        result = runner.invoke(cli.stilus,
                               ['--out', 'some_directory',
                                'foo.styl', 'foo.css'])
        css_file = Path(fs) / Path('some_directory') / Path('foo.css')
        assert css_file.exists() is True
        assert css_file.read_text() == css
        assert result.exit_code == 0
        assert result.output == ''
        result = runner.invoke(cli.stilus,
                               ['--out', 'some_directory', '-p',
                                'foo.styl', 'foo.css'])
        css_file = Path(fs) / Path('some_directory') / Path('foo.css')
        assert css_file.exists() is True
        assert css_file.read_text() == css
        assert result.exit_code == 0
        assert result.output == css
