from pathlib import Path

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
        # print('.', end='')
    # print()


if __name__ == '__main__':
    # source_file = Path('./cases/vargs.styl.later')
    # with open(source_file, 'r') as f:
    #     source = f.read()
    # with open(source_file.with_suffix('.css'), 'r') as f:
    #     destination = f.read()
    # print(f'source: {source}')
    # result = Renderer(source, {}).render()
    # print(f'result: [{result}].')
    # print(Renderer(source, {}).render())
    # assert destination == Renderer(source, {}).render()
    #     source = """
    # padding(y, rest...)
    #   test-y y
    #   if rest
    #     padding rest
    #
    # body
    #   padding 1px
    #   padding 1px 2px 3px
    #
    # foo(args...)
    #   bar: args
    #
    # body
    #   foo 1 2 3
    #   foo 1, 2, 3
    # """
    source = """
  box-shadow(args...)
    -webkit-box-shadow args
    -moz-box-shadow args
    box-shadow args

  #login
    box-shadow 1px 2px 5px #eee
"""
    #     source = """
    # add(a, b)
    #   a + b
    #
    # body
    #   padding add(5, 2)
    #   padding add(10, 20)
    #   padding add(100, 100)
    #   padding add(10, -5)
    #   foo
    #     foo add(10, 10)
    #     foo add(10, 20)
    #   middle add(1, 0)
    #   bar
    #     bar add(100, 1000)
    #     bar add(100, 500)
    # head
    #   padding add(10, 3)
    # """
    #     source = """
    # body
    #   foo unit(20, 'px')
    #   foo unit(20, px)
    #   foo unit(20%, px)
    #   foo unit(20, '%')
    # """
    result = Renderer(source, {}).render()
    print(f'result: {result}.')
    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(Renderer(source, {}).render())
