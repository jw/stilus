from pathlib import Path

import pytest

from stilus.stilus import Renderer

files = []
path = Path.joinpath(Path.cwd(), 'tests', 'stylus', 'cases')
styl_files = path.glob('*.styl')
for f in styl_files:
    files.append((str(f), str(f.with_suffix('.css'))))


@pytest.mark.parametrize("styl,css", files)
def test_stylus_cases(styl, css):
    with open(styl, 'r') as f:
        source = f.read()
    with open(css, 'r') as f:
        destination = f.read()

    stylus = Path.joinpath(Path.cwd(), 'tests', 'stylus')
    images = stylus / 'images'
    jsons = stylus / 'cases'
    renderer = Renderer(source, {}).include(images).include(jsons)

    assert renderer.render() == destination
