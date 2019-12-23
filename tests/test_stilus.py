from functions.resolver import get_resolver
from renderer import Renderer
from stilus import renderer


def test_stylus():
    source = 'abc\n  color: red\n'
    css = 'abc {\n  color: #f00;\n}\n'
    assert renderer.render(source, {}) == css
    source = '\nsize = 12px\n\nbody\n  font-size: size\n\n'
    css = 'body {\n  font-size: 12px;\n}\n'
    assert renderer.render(source, {}) == css
    source = '\nsize = 12px\n\nbody\n  font-size size\n\n'
    css = 'body {\n  font-size: 12px;\n}\n'
    assert renderer.render(source, {}) == css


def run_test_case(source, destination):
    with open(source, 'r') as f:
        source = f.read()
    with open(destination, 'r') as f:
        destination = f.read()

    renderer = Renderer(source, {})
    renderer.include('/home/jw/python/projects/stilus/tests/stylus/images')
    renderer.include('/home/jw/python/projects/stilus/tests/stylus/cases')

    css = renderer.render()

    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')

    assert destination == css


if __name__ == '__main__':

    source = """
op(a, b=a, operator='+')
  arguments

body
  foo: op(1) // 1 1 +
  foo: op(1, 5) // 1 5 +
  foo: op(1, 5, '-') // 1 5 -

op(a, rest...)
  arguments

body
  foo: op(1) // 1
  foo: op(1, 2) // 1 2
  foo: op(1, 2, 3) // 1 2 4
  foo: op(1, 2, 3, 4 5 6) // 1 2 3 4 5 6
"""

    source = """
@media screen
  .foo
    @media (max-width: 499px)
      width: 200px;
    @media (min-width: 500px)
      width: 50%;
    @media (min-width: 900px)
      width: 25%;
"""

    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(f'{ast}')

    stylus_path = '/home/jw/python/projects/stilus/tests/stylus'
    r = Renderer(source, {})
    r.include(f'{stylus_path}/cases')
    r.include(f'{stylus_path}/images')
    r.include(f'{stylus_path}/cases/import.basic')
    r.include(f'{stylus_path}/imports')
    r.include('.')

    r.define('url', get_resolver(), raw=True, options={'nocheck': True})
    r.options['include css'] = True

    # r.options['compress'] = True
    # r.options['hoist atrules'] = True

    css = r.render()

    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')
