from pathlib import Path

from stilus.stilus import Renderer


def test_stylus_cases():
    path = Path('./cases')
    source_files = path.glob('*.styl')
    for source_file in source_files:
        with open(source_file, 'r') as f:
            source = f.read()
        with open(source_file.with_suffix('.css'), 'r') as f:
            destination = f.read()
        assert destination == Renderer(source, {}).render()
