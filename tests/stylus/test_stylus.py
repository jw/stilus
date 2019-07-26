from pathlib import Path

from bin.stilus import setup_logging
from stilus.stilus import Renderer


# todo: add dot per styl -> css compilation
# see: https://docs.pytest.org/en/latest/example/parametrize.html#paramexamples
def test_stylus_cases():
    path = Path('/home/jw/python/projects/stilus/tests/stylus/cases')
    source_files = path.glob('*.styl')
    for source_file in source_files:
        # print(f'Handling {source_file}...', end='')
        with open(source_file, 'r') as f:
            source = f.read()
        with open(source_file.with_suffix('.css'), 'r') as f:
            destination = f.read()
        assert destination == Renderer(source, {}).render()
        # print('.')
        # print('.', end='')
    # print()


if __name__ == '__main__':
    setup_logging('bin/logging.yaml')

    # source_file = Path('./cases/bifs.darken.styl')
    # with open(source_file, 'r') as f:
    #     source = f.read()
    # with open(source_file.with_suffix('.css'), 'r') as f:
    #     destination = f.read()
    # # print(f'source: {source}')
    # result = Renderer(source, {}).render()
    # print(f'result: [{result}].')
    source = """
box-shadow(args...)
    -webkit-box-shadow args
    -moz-box-shadow args
    box-shadow args

#login
    box-shadow 1px 2px 5px #eee
    body
        box-shadow 100px 100px 3px red
"""
    source = """
body
  foo bar
  foo complement(#f00)
"""
    result = Renderer(source, {}).render()
    print(f'------------------- result ---')
    print(f'{result}')
    print(f'------------------------------')
    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(Renderer(source, {}).render())
