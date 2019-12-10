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

    sourced = """

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

    source = """
.tester
  color #FFF

$tester2
  font-size 12px

$tester3
  border-radius 1px

.end
  @extend .tester !optional, notExist1 !optional,
  $notExist2 !optional, $tester2 !optional, {'$test' + 'er3'} !optional
  border #AAA
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
    # r.options['hoist atrules'] = True

    css = r.render()

    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')
