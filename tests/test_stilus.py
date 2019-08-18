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
font-size-2 = 10px
font-size-3 = 20px
font-size-4 = 30px
font-size-5 = 40px

for i in 3..2
  .text-{i}
    font-size: lookup('font-size-' + i)
"""
    source = """

string(val)
  '' + val

replace(expr, str, val)
  expr[i] = val if string(e) == str for e, i in expr

linear-gradient(from, to) {
  if current-property {
    webkit = s('-webkit-gradient(linear, 0% 0%, 0% 100%,
                                 from(%s), to(%s))', from, to);
    moz = s('-moz-linear-gradient(%s, %s)', from, to);
    prop = current-property;
    replace(current-property[1], '__CALL__', moz);
    // add-property(prop[0], prop[1]);
    // webkit;
  } else {
    error('linear-gradient() must be used within a property');
  }
}

body
  background foo linear-gradient(#2a2a2a, #454545) bar

"""
    source = """
prefix = 'border'

define('border', {
  color: #000,
  length: 1px,
  style: solid
})

for prop, val in border
  define(prefix + '-' + prop, val)

body
  border: border-length border-style border-color
"""
    source = """
fonts = Arial, sans-serif
 p('test')
 p(123)
 p((1 2 3))
 p(fonts)
 p(#fff)
 p(rgba(0,0,0,0.2))

 add(a, b)
   a + b

 p(add)
"""

    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(f'{ast}')

    css = stilus.render(source, {})
    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')
