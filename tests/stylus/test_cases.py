from pathlib import Path

import pytest

from bin.stilus import setup_logging
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
    assert destination == Renderer(source, {}).render()


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

test(args...)
  test-args args
  for arg in args
    foo arg

size(a, b)
  return a b

body
  test 1 2 3
  test (1 2) (3 4) 5
  test size(1, 2) size(3, 4)

body
  sizes = size(1, 2) size(3, 4)
  for size in sizes
    foo size

body
  for n in 1..5
    foo n

body
  for n in 1 2 3
    foo n

body
  for n in 1 2 3
    foo
      bar n
"""
    """
func(num)
  return num

body
  for n in 1 2 3
    bar func(num: n)

test(args...)
  foo
    for arg in args
      bar
        baz arg

body
  test 1 2 3

body
  for val, index in foo bar baz
    foo index val

"""
    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(f'{ast}')
    result = Renderer(source, {}).render()
    print(f'------------------- result ---')
    print(f'{result}')
    print(f'------------------------------')
