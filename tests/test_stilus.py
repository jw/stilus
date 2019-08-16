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
    # source = '\nsize = 12px\n\nbody\n  font-size: size\n\n'
    # css = 'body {\n  font-size: 12px;\n}\n'
    # assert stilus.render(source, {}) == css

    source = """
font-size-2 = 10px
font-size-3 = 20px
font-size-4 = 30px
font-size-5 = 40px

for i in 2..5
  .text-{i}
    font-size: lookup('font-size-' + i)
"""
    """
"$foo = 'screen'
body
  bar $foo
@media $foo
  .i
    test: $foo
"""
    source = """
foo(i)
  width: i

.test
  foo(i) for i in 1..10
"""
    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(f'{ast}')

    css = stilus.render(source, {})
    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')
