import logging
import logging.config
import os
import sys
import time
from pathlib import Path
from typing import Optional, List

import click
import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from __version__ import __version__
from renderer import Renderer

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def setup_logging(default_path='logging.yaml',
                  default_level=logging.INFO,
                  env_key='STILUS_LOGGING_CONFIG'):
    """Setup logging configuration.
    :param default_path: The path to the yaml logging config file.
    :param default_level: The default level is ``logging.INFO``.  Only used
                          when the ``default_path`` is not found.
    :param env_key: The environment property to be used as default_path.
    """
    path = os.getenv(env_key, default_path)
    p = Path(path)
    if p.exists():
        with open(path) as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        logging.debug(f'Using {p.resolve()} as logging configuration file.')
    else:
        logging.basicConfig(level=default_level)
        logging.warning('Using default logging configuration.')


setup_logging('bin/logging.yaml')


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'{__version__}')
    ctx.exit()


def validate_path(ctx, param, value):
    return Path(value)


def fail(message, prefix=None, code=-1):
    if not prefix:
        prefix = '     error '
    click.echo(click.style(prefix, fg='red'), nl=False)
    click.echo(message)
    sys.exit(code)


def fancy_output(message, prefix=None):
    if prefix:
        click.echo(click.style(prefix, dim=True), nl=False)
    click.echo(message)


def render(source: str, includes=None, compress=False) -> str:
    """
    Render a source str to css.
    :param source: A Stylus source string.
    :type source: str
    :param includes: List of directories to include.
    :type includes: list, optional
    :param compress: Compress the output?  False by default.
    :type compress: bool, optional
    :return: The resulting css.
    :rtype: str
    """
    if not includes:
        includes = []
    renderer = Renderer(source, {'compress': compress})
    for include in includes:
        # todo: check existence?
        renderer.include(include)
    return renderer.render()


def write_result(css, path):
    p = Path(path).resolve()
    with p.open(mode='w+'):
        p.write_text(css)


def compile(source: Path,
            path: Path = None,
            includes: Optional[List[Path]] = None,
            compress: bool = False) -> None:
    """
    Compile a source Path.  If path is given compile to that path,
    otherwise compile into the same folder.
    :param source: A Stylus source Path.
    :type source: Path
    :param path: The path to compile to.
    :type path: Path, optional
    :param includes: List of directories to include.
    :type includes: list, optional
    :param compress: Compress the output?  False by default.
    :type compress: bool, optional
    """
    if path:
        destination = path / Path(source.name).with_suffix('.css')
    else:
        destination = source.with_suffix('.css')
    # todo: check includes existence here?
    css = render(source.read_text(), includes, compress)
    write_result(css, destination)
    fancy_output(str(destination), prefix='  compiled ')
    logging.info(f'Compiled {destination}.')


def prepare_watch(path: Path,
                  include: Optional[List[Path]] = None,
                  compress: bool = False) -> List[Path]:
    """
    Compile all Stylus files in the given path and recompile
    automatically when these files change.
    :param path: A path.
    :type path: Path
    :param includes: List of directories to include.
    :type includes: list, optional
    :param compress: Compress the output?  False by default.
    :type compress: bool, optional
    :return: List of paths that are present in the given Path
    :rtype: List[Path]
    """
    if not include:
        include = []
    logging.info(f'Watching {path}...')
    styles = list(path.glob('*.styl'))
    logging.info(f'{styles}')
    for styl in styles:
        fancy_output(str(styl), prefix='  watching ')
        compile(styl, path, include, compress)
    return styles


def check_out(out: str) -> None:
    """
    Check of the given out str is an existing directory.  Otherwise
    fiail
    :param out: A possibly existing directory
    :type out: str
    """
    if not Path(out).exists():
        fail(f'Directory not found: {out}.')
    elif not Path(out).is_dir():
        fail(f'{out} is not a directory.')


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('input', type=click.File('r'), required=False)
@click.argument('output', type=click.File('w'), required=False)
@click.option('-v', '--verbose', count=True, help='Be more verbose.')
@click.option('-w', '--watch', is_flag=True, default=False,
              help='Watch file(s) for changes and re-compile.')
@click.option('-c', '--compress', is_flag=True, default=False,
              help='Compress CSS output.')
@click.option('-p', '--print', 'print_', is_flag=True, default=False,
              help='Print out the compiled CSS.')
@click.option('-I', '--include', multiple=True,
              help='Add <path> to lookup paths.')
@click.option('-o', '--out',
              help='Output to <dir> when passing files.')
@click.option('--version', '-V', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Display the version of Stilus.')
def stilus(verbose, watch, compress, print_, include, out, input, output):

    class StilusHandler(FileSystemEventHandler):
        def on_modified(self, event):
            path = Path(event.src_path)
            if path in styles:
                compile(path, None, include, compress)

    if out:
        check_out(out)
        logging.info(f'Redirecting results to {out}.')

    if watch:
        path = Path.cwd()
        styles = prepare_watch(path, compress, include)
        event_handler = StilusHandler()
        observer = Observer()
        observer.schedule(event_handler, path=str(path), recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(.25)
        except KeyboardInterrupt:
            logging.info('Bailing out...')
            observer.stop()
        observer.join()
    else:
        if not input:
            input = click.get_text_stream('stdin')
            logging.info('Reading from stdin...')
        if not output:
            output = click.get_text_stream('stdout')
            logging.info('Writing to stdout...')
        elif out:
            output = (Path(out) / Path(output.name)).open('w')
            logging.info(f'Writing to {output}.')
        css = render(input.read(), include, compress)
        if print_:
            click.echo(css, nl='\n' if compress else '')
        output.write(css)


if __name__ == '__main__':
    stilus()
