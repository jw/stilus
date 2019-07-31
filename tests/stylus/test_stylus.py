from pathlib import Path

from bin.stilus import setup_logging
# from stilus.parser import Parser
from stilus.stilus import Renderer


# todo: add dot per styl -> css compilation
# see: https://docs.pytest.org/en/latest/example/parametrize.html#paramexamples
def test_stylus_cases():
    path = Path.joinpath(Path.cwd(), 'tests', 'stylus', 'cases')
    source_files = path.glob('*.styl')
    for source_file in source_files:
        print(f'Handling {source_file}...', end='')
        with open(source_file, 'r') as f:
            source = f.read()
        with open(source_file.with_suffix('.css'), 'r') as f:
            destination = f.read()
        assert destination == Renderer(source, {}).render()
        print('.')
        # print('.', end='')
    # print()


if __name__ == '__main__':
    setup_logging('bin/logging.yaml')
    source = """
string(val)
  '' + val

replace(expr, str, val)
  expr[i] = val if string(e) == str for e, i in expr

linear-gradient(from, to) {
  if current-property {
    webkit = s('-webkit-gradient(linear, 0% 0%, 0% 100%, from(%s), to(%s))',
    from, to);
    moz = s('-moz-linear-gradient(%s, %s)', from, to);
    prop = current-property;
    replace(current-property[1], '__CALL__', moz);
    add-property(prop[0], prop[1]);
    webkit;
  } else {
    error('linear-gradient() must be used within a property');
  }
}

body
  background fizz linear-gradient(#2a2a2a, #454545) fuzz
"""
    source = """
body
  foo blend(rgba(0, 0, 0, 0.5))
"""
    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(f'{ast}')
    result = Renderer(source, {}).render()
    print(f'------------------- result ---')
    print(f'{result}')
    print(f'------------------------------')
