from stilus import stilus


def test_stylus():
    source = 'abc\n  color: red\n'
    css = 'abc {\n  color: #f00;\n}\n'
    assert stilus.render(source, {}) == css
    source = '\nsize = 12px\n\nbody\n  font-size: size\n\n'
    css = 'body {\n  font-size: 12px;\n}\n'
    assert stilus.render(source, {}) == css
    source = '\nsize = 12px\n\nbody\n  font-size size\n\n'
    css = 'body {\n  font-size: 12px;\n}\n'
    assert stilus.render(source, {}) == css


if __name__ == '__main__':
    source = """
padding(y, rest...)
  test-y y
  if rest
    padding rest

body
  padding 1px 2px 3px
"""
    source = '\nsize = 12px\n\nbody\n  font-size: size\n\n'
    css = 'body {\n  font-size: 12px;\n}\n'
    assert stilus.render(source, {}) == css

    source = """   
size = 12px
large = size * (3 - 1)
huge = size * 3

body
  font-size size

h1
  font-size huge

h2
  font-size large
  font 5px % 3
  font 5px % 5
  font 2px ** 4
  y = 10
  x = 15

body {
  foo: 50% * 2;
  foo: 2 * 50%;
  foo: 50 + 50%;
  foo: 50 - 50%;
  foo: 50% - 50%;
  foo: 50% + 20%;
}
body {
  foo: 5 + 5em;
  foo: 5em + 5;
}
"""
    css = stilus.render(source, {})
    print(f'result:\n[{css}]')
