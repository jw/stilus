import logging
import logging.config
import os
from pathlib import Path

import click
import yaml

from stilus.stilus import Renderer


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
    from stilus import __version__
    click.echo(f'{__version__}')
    ctx.exit()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', count=True)
@click.option('-p', '--print', 'print_', is_flag=True, default=False,
              help='Print out the compiled CSS.')
@click.option('-I', '--include', help='Add <path> to lookup paths.')
@click.argument('input', type=click.File('r'))
@click.argument('output', required=False,
                type=click.Path(dir_okay=False,
                                writable=True))
@click.option('--version', '-V', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Display the version of Stilus.')
def cli(verbose, print_, include, input, output=None):
    renderer = Renderer(input.read(), {})
    css = renderer.render()
    if print_ or not output:
        click.echo(css)
    if output:
        p = Path(output).resolve()
        with p.open(mode='w+'):
            p.write_text(css)


if __name__ == '__main__':
    cli()
