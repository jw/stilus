from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from click.testing import CliRunner

from stilus import __version__
from stilus import cli


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


def test_cli_prefix():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('foo.styl', 'w') as f:
            f.write('for n in 1 2 3\n'
                    '  .grid-{n}\n'
                    '    width: unit(n * 100, \'px\')\n')
        result = runner.invoke(cli.stilus, ['-P', 'hello-', 'foo.styl'])
        assert result.exit_code == 0
        assert result.output == '.hello-grid-1 {\n' \
                                '  width: 100px;\n' \
                                '}\n' \
                                '.hello-grid-2 {\n' \
                                '  width: 200px;\n' \
                                '}\n' \
                                '.hello-grid-3 {\n' \
                                '  width: 300px;\n' \
                                '}\n'


def test_cli_hoist_atrules():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('foo.styl', 'w') as f:
            f.write('body\n'
                    '  foo bar\n'
                    '@charset \'utf-8\'\n')
        result = runner.invoke(cli.stilus, ['--hoist-atrules', 'foo.styl'])
        assert result.exit_code == 0
        assert result.output == '@charset \'utf-8\';\n' \
                                'body {\n' \
                                '  foo: bar;\n' \
                                '}\n'


def test_fail(capsys):
    with pytest.raises(SystemExit) as e:
        cli.fail('Hello there!', code=42)
    captured = capsys.readouterr()
    assert 'Hello there!' in captured.out
    assert e.type == SystemExit
    assert e.value.code == 42

    with pytest.raises(SystemExit) as e:
        cli.fail('Hello there!')
    assert e.type == SystemExit
    assert e.value.code == -1


def test_fancy_output(capsys):
    cli.fancy_output('Some fancy output')
    captured = capsys.readouterr()
    assert 'Some fancy output' in captured.out

    cli.fancy_output('Some fancy output', 'hello')
    captured = capsys.readouterr()
    assert 'hello' in captured.out
    assert 'Some fancy output' in captured.out


def test_prepare_watch():
    with TemporaryDirectory() as td:
        path = Path(td)
        with open(path / 'foo.styl', 'w') as f:
            f.write('foo\n  abc blue\n')
        with open(path / 'bar.styl', 'w') as f:
            f.write('bar\n  def red\n')
        styles = cli.prepare_watch(path, None, [])
        assert sorted(styles) == sorted([path / 'foo.styl',
                                        path / 'bar.styl'])
        assert sorted(list(path.glob('*.css'))) == sorted([path / 'foo.css',
                                                           path / 'bar.css'])
