from pathlib import Path

import pytest
import logging

from functions.resolver import get_resolver
from renderer import Renderer

log = logging.getLogger(__name__)


files = []
path = Path.joinpath(Path.cwd(), 'tests', 'stylus', 'cases')
styl_files = path.glob('**/*.styl')
for f in styl_files:
    if 'import.' in str(f.parent):  # skip the import directories
        continue
    css_file = f.with_suffix('.css')
    if css_file.exists():
        files.append((f, css_file))


def idfn(val):
    if isinstance(val, Path):
        return str(val)


@pytest.mark.parametrize("styl,css", files, ids=idfn)
def test_stylus_cases(styl, css):
    with styl.open(encoding='utf-8') as f:
        source = f.read()
    with css.open(encoding='utf-8') as f:
        destination = f.read()

    # first create include folders
    stylus = Path.cwd() / 'tests' / 'stylus'
    images = stylus / 'images'
    basics = stylus / 'cases' / 'import.basic'
    cases = stylus / 'cases'
    imports = cases / 'imports'

    renderer = Renderer(source, {})

    renderer.include(cases)
    renderer.include(images)
    renderer.include(basics)
    renderer.include(imports)

    # add options based on the test names

    if 'include.' in styl.name:
        renderer.options['include css'] = True

    if 'compress.' in styl.name or 'compressed.' in styl.name:
        renderer.options['compress'] = True

    if 'prefix.' in styl.name:
        renderer.options['prefix'] = 'prefix-'

    if 'hoist.' in styl.name:
        renderer.options['hoist atrules'] = True

    if 'resolver.' in styl.name:
        renderer.define('url', get_resolver(),
                        raw=True, options={'nocheck': True})

    log.debug(f'Testing styl: {styl.name}; '
              f'include: {"include." in styl.name}; '
              f'compress: {"compress." in styl.name}; '
              f'prefix: {"prefix." in styl.name}; '
              f'hoist: {"hoist." in styl.name}; '
              f'resolver: {"resolver." in styl.name};'
              f'options: {renderer.options};'
              f'functions {renderer.options["functions"]}.')

    assert renderer.render() == destination
