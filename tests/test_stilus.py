# from functions.resolver import get_resolver
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
@import url('http://foo.com/foo.css')
@import url("http://foo.com/foo.css")
@import url('https://foo.com/foo.css')
@import url('//foo.com/foo.css')
@import "http://foo.com/foo.css"
@import 'https://foo.com/foo.css'
@import '//foo.com/foo.css'
@import 'http://foo.com/foo.css'
@import url('#')
"""

    source = """
@import url("foo.css")
"""

    source = """
@import "import.include.resolver.nested/b/b"
extend_a()
"""

    source = """
.embed-with-utf8 {
  color: #c00;
  background: embedurl("circle.svg", "utf8");
}

.too-big-no-hash {
  color: #c00;
  background: url("tiger.svg");
}

body
  foo url('#')
"""

    source = """

width(img)
  return image-size(img)[0]

height(img)
  return image-size(img)[1]

body
  foo image-size('gif')
  foo image-size('gif')[0] == width('gif')
  foo image-size('gif')[1] == height('gif')

body
  foo image-size('tux.png')
  foo image-size('tux.png')
  bar image-size('flowers.jpeg')
  bar image-size('flowers_p.jpg')
  baz image-size('tiger.svg')

body
  foo image-size('foo.png', true)

// Checking for the file, so we could do a fallback
body.tux
  if image-size('tux.png', true)
    background: url('tux.png')
  else
    background: lime

body.foo
  if image-size('foo.png', true)
    background: url('foo.png')
  else
    background: lime
"""

    source = """
@import "a"
@import url(foo.css)
@import url('foo.css')
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

    # r.define('url', get_resolver(), raw=True, options={'nocheck': True})
    r.options['include css'] = True

    # r.options['compress'] = True
    # r.options['hoist atrules'] = True

    css = r.render()

    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')
