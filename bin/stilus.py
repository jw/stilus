import logging
import logging.config
import os
from pathlib import Path

import click
import yaml


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
    from __version__ import __version__
    click.echo(f'Version {__version__}')
    ctx.exit()


@click.command()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
def hello():
    logging.info(f'An info message!')
    click.echo(f'This still needs some work 8-)')
    logging.debug(f'Some debug message.')


if __name__ == '__main__':
    hello()
