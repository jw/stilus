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

nums = 1

append(nums, 2)
append(nums, 3, 4, 5)

body
  foo: nums
  foo: nums[0]
  foo: nums[4]

nums = 1

push(nums, 2)

body
  foo: ret = push(nums, 3, 4, 5)
  foo: nums[0]
  foo: nums[4]


nums = 3

body
  foo: unshift(nums, 2, 1)
  foo: nums

list = ()

body
  foo: push(list, foo, bar, baz)
  foo: push(list, foo, bar, baz)
  foo: list

list = (one 1)
push(list, two 2, three 3)

body
  foo: list

func(list)
  push(list, 3,4,5)

nums = 1 2
func(nums)

body
  foo: nums

func()
  list = ()

  for arg in arguments
    foo: arg
    push(list, arg)

body
  func: 1, 2, 3
"""

    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(f'{ast}')

    css = stilus.render(source, {})
    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')
