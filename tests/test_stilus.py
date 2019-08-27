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
font-size-2 = 10px
font-size-3 = 20px
font-size-4 = 30px
font-size-5 = 40px

body
    font-size: lookup('font-size-' + 2)
    font-size: lookup('font-size-' + 3)

for i in 3..2
    foo: i
    font-size: lookup('font-size-' + i)

for i in 3..2
  .text-{i / 10}
    foo: i
    font-size: lookup('font-size-' + i)
"""

    source = """
font-size-2 = 10px
font-size-3 = 20px
font-size-4 = 30px
font-size-5 = 40px

for i in 100..99
  .text-{i}
    foo: i
    // font-size: lookup('font-size-' + i)
"""

    source = """
list = red green blue
no-colors = false

body
  color: color for color in list if length(list) > 2 unless no-colors

mixin()
  color: color for color in list if length(list) > 2 unless no-colors

body
  mixin()
"""
    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(f'{ast}')

    css = stilus.render(source, {})
    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')
