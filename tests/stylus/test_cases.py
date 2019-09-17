from pathlib import Path

import pytest

from stilus.stilus import Renderer

files = []
path = Path.joinpath(Path.cwd(), 'tests', 'stylus', 'cases')
styl_files = path.glob('*.styl')
for f in styl_files:
    css_file = f.with_suffix('.css')
    if css_file.exists():
        files.append((str(f), str(css_file)))


@pytest.mark.parametrize("styl,css", files)
def test_stylus_cases(styl, css):
    with open(styl, 'r') as f:
        source = f.read()
    with open(css, 'r') as f:
        destination = f.read()

    stylus = Path.joinpath(Path.cwd(), 'tests', 'stylus')
    images = stylus / 'images'
    basics = stylus / 'cases' / 'import.basic'
    cases = stylus / 'cases'

    renderer = Renderer(source, {})
    renderer.include(images)
    renderer.include(basics)
    renderer.include(cases)
    renderer.options['include css'] = True

    assert renderer.render() == destination
