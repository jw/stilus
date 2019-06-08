import logging
from pathlib import Path

from stilus.parser import Parser
from stilus.stilus import Renderer

log = logging.getLogger(__name__)


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
        result = Renderer(source, {}).render()
        assert destination == Renderer(source, {}).render()
        # print('.', end='')
    # print()


if __name__ == '__main__':
    source_file = Path('./cases/vargs.styl.later')
    with open(source_file, 'r') as f:
        source = f.read()
    with open(source_file.with_suffix('.css'), 'r') as f:
        destination = f.read()
    result = Renderer(source, {}).render()
    print(f'result: [{result}].')
    print(Renderer(source, {}).render())
    assert destination == Renderer(source, {}).render()
#     source = """
# padding(y, rest...)
#   y y
#   if rest
#     padding rest
#
# body
#   padding 1px 2px 3px
# """
#     source = """
#   box-shadow(args...)
#     -webkit-box-shadow args
#     -moz-box-shadow args
#     box-shadow args
#
#   #login
#     box-shadow 1px 2px 5px #eee
# """
#     source = """
# add(a, b)
#   a + b
# body
#   padding add(5, 2)
# head
#   padding add(10, 3)
# """
#     result = Renderer(source, {}).render()
#     print(f'result: {result}.')
    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(Renderer(source, {}).render())
