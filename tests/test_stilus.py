from stilus import renderer
from renderer import Renderer


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

    # if.mixin.styl
    source = """
test(n)
  if n < 0
    got below
  else
    got above

test-nested(a, b)
  if a > 1
    if unit(-5) == ''
      got empty
      yup just lots of empty
    else
      got unit(-5px)

test-unless(n = 0)
  unless n
    padding 10px

body
  test(5px)
  test(-5px)
  test-nested(5px, -5)
  test-unless()

foo()
  $width = 10px
  .foo
    if true
      width: $width

foo()

bar()
  @font-face
    font-family foo
    if true
      src bar

  @page
    margin 0
    if true
      padding 0

bar()
"""

    source = """

pad(size = small)
  if large == size
    padding 20px
  if medium == size
    padding 10px
  if small == size
    padding 3px

body
  pad(large)
  pad(medium)
  pad()
  pad(invalid)

nested(val)
  if val
    foo bar
    bar baz
    .two
      level two
      &:hover
        level three

form input
  nested(true)
  nested(false)

break()
  foo bar
  bar baz
  return
  baz raz

body
  break()
"""

    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(f'{ast}')

    stylus_path = '/home/jw/python/projects/stilus/tests/stylus'
    r = Renderer(source, {})
    r.include(f'{stylus_path}/images')
    r.include(f'{stylus_path}/cases')
    r.include(f'{stylus_path}/cases/import.basic')
    r.include(f'{stylus_path}/imports')
    r.include('.')

    # r.options['include css'] = True
    # r.options['compress'] = True
    r.options['hoist atrules'] = True

    css = r.render()

    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')
