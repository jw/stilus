from pathlib import Path

import pytest

from functions.resolver import get_resolver
from renderer import Renderer

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

    renderer = Renderer(source, {'paths': ['.']})

    # first create include folders
    stylus = Path.joinpath(Path.cwd(), 'tests', 'stylus')
    images = stylus / 'images'
    basics = stylus / 'cases' / 'import.basic'
    cases = stylus / 'cases'
    imports = cases / 'imports'

    renderer.include(images)
    renderer.include(basics)
    renderer.include(cases)
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
        renderer.define('url', get_resolver({'nocheck': True}), raw=True)

    assert renderer.render() == destination


if __name__ == '__main__':
    base = Path('/home/jw/python/projects/stilus/tests/stylus/cases')
    styl = base / 'regressions' / 'regression.1277.styl'
    css = base / 'regressions' / 'regression.1277.css'

    with styl.open(encoding='utf-8') as f:
        source = f.read()
    with css.open(encoding='utf-8') as f:
        destination = f.read()

    # first create include folders
    stylus = Path.joinpath(Path.cwd())
    print(f'stylus: {stylus}')
    images = stylus / 'images'
    basics = stylus / 'cases' / 'import.basic'
    cases = stylus / 'cases'
    imports = stylus / 'imports'

    renderer = Renderer(source, {'paths': ['.']})
    renderer.include(images)
    renderer.include(basics)
    renderer.include(cases)
    renderer.include(imports)

    # renderer.options['include css'] = True
    # if 'compress' in styl.name:
    #     renderer.options['compress'] = True

    result = renderer.render()

    stylus_path = '/home/jw/python/projects/stilus/tests/stylus'
    r = Renderer(source, {})
    r.include(f'{stylus_path}/images')
    r.include(f'{stylus_path}/cases')
    r.include(f'{stylus_path}/cases/import.basic')
    r.include(f'{stylus_path}/imports')
    r.include('.')

    # r.options['include css'] = True
    # r.options['compress'] = True
    # r.options['hoist atrules'] = True

    css = r.render()

    assert result == destination
