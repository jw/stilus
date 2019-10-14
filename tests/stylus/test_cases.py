from pathlib import Path

import pytest

from stilus.stilus import Renderer

files = []
path = Path.joinpath(Path.cwd(), 'tests', 'stylus', 'cases')
styl_files = path.glob('*.styl')
for f in styl_files:
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
    stylus = Path.joinpath(Path.cwd(), 'tests', 'stylus')
    images = stylus / 'images'
    basics = stylus / 'cases' / 'import.basic'
    cases = stylus / 'cases'

    renderer = Renderer(source, {})
    renderer.include(images)
    renderer.include(basics)
    renderer.include(cases)
    renderer.options['include css'] = True

    if 'compress' in styl.name:
        renderer.options['compress'] = True

    result = renderer.render()

    assert result == destination
