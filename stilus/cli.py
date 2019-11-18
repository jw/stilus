import logging
import logging.config
import os
import sys
import time
from pathlib import Path

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

    def render(source, includes):
        renderer = Renderer(source, {'compress': compress})
        for include in includes:
            # todo: check existence?
            renderer.include(include)
        return renderer.render()

    def write_result(css, path):
        p = Path(path).resolve()
        with p.open(mode='w+'):
            p.write_text(css)

    def compile(source, path, includes):
        css = render(source, includes)
        destination = path.with_suffix('.css')
        write_result(css, destination)
        fancy_output(str(destination), prefix='  compiled ')
        logging.info(f'Compiled {path}.')

    class StilusHandler(FileSystemEventHandler):
        def on_modified(self, event):
            path = Path(event.src_path)
            if path in styles:
                source = path.read_text()
                compile(source, path)

    if out:
        if not Path(out).exists():
            fail(f'Directory not found: {out}.')
        elif not Path(out).is_dir():
            fail(f'{out} is not a directory.')
        logging.info(f'Redirecting results to {out}.')

    if watch:
        path = Path.cwd()
        logging.info(f'Watching {path}...')
        styles = list(path.glob('*.styl'))
        for styl in styles:
            fancy_output(str(styl), prefix='  watching ')
            source = styl.read_text()
            compile(source, path, include)
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
        css = render(input.read(), include)
        if print_:
            click.echo(css, nl='\n' if compress else '')
        output.write(css)


if __name__ == '__main__':
    stilus()
