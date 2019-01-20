from pathlib import Path
from stilus.stilus import Renderer
import logging

log = logging.getLogger(__name__)


# todo: add dot per styl -> css compilation
#  https://docs.pytest.org/en/latest/example/parametrize.html#paramexamples
def test_stylus_cases():
    path = Path('./stylus/cases')
    source_files = path.glob('*.styl')
    for source_file in source_files:
        # print(f'Handling {source_file}...', end='')
        with open(source_file, 'r') as f:
            source = f.read()
        with open(source_file.with_suffix('.css'), 'r') as f:
            destination = f.read()
        assert destination == Renderer(source, {}).render()
        # print('.', end='')
    # print()
