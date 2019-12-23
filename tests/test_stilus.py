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

obj = {
  foo: 'bar',
  bar: 'baz',
  baz: 'raz'
  'qux': 'qux'
}

body
  // foo: obj.foo.bar
  foo: obj.foo
  foo: obj.bar
  foo: obj.foo obj.baz obj.baz
  list = obj.foo obj.bar
  foo: list
  qux: obj.qux
  bar: length(obj)
  str: obj

body
  foo: type(obj)
  bar: 'foo' in obj
  baz: 'something' in obj
  for prop, value in obj
    {prop}: obj[prop]
    {prop}: value
  if 'bar' in obj
    color: #c00

sizes = {
  small: .25em .35
  medium: .5em .7em
  large: 1em 1.4em
}

body
  foo: sizes.small
  foo: sizes.small sizes.medium
  foo: sizes.small[0] sizes.small[1]
  foo: sizes.small[0] + sizes.small[1]
  sizes: keys(sizes)
  sizes: values(sizes)

foo = {
  bar: {
    baz: {
      raz: Wahoo
    }
  }
}

body
  foo: foo.something == null
  foo: foo.bar.baz.raz

tobi = { name: Tobi }
jane = { name: Jane, friend: tobi }
user = tobi
another = user

body
  foo: jane.name
  foo: user.name
  foo: another.name
  foo: jane.friend.name
  foo: operate('.', jane, 'name')
  foo: operate('[]', user, 'name')
  // foo: jane.friend.name.something

body
  tobi = { name: Tobi, age: 2 }
  foo: tobi.name, a tobi.age year old ferret

tobi['species'] = { kind: Ferret }
tobi['food'] = apple potato nuts

body
  foo: tobi.species.kind
  bar: tobi['species']['kind']
  baz: tobi.food[2]

if true {
  obj = {
    color: #0c0
  }

  body {
    color: obj.color
  }
}

for num in 1..3 {
  obj = {
    color: num
  }

  body {
    color: obj.color
  }
}

empty = {}

body
  if empty
    color: red
  else
    color: blue

bar = {}
body
  if true
    bar[length(bar['baz'])] = 'raz'

obj = {
  /* margin */
  foobar: 10px

  /* height */
  ,bar  : 40px

  ,  baz /* comment */  : 500px
}

body
  margin: obj.foobar
  height: obj.bar
  width: obj.baz

obj1 = {}
obj2 = { foo: 1, bar: 2 }

body
  test: obj1 == obj2
  test: obj2 != obj1
  test: obj1 == {}
  test: obj2 == { foo: 1, bar: 2 }

  obj2.qux = { baz: 1 }
  test: obj2 == { foo: 1, bar: 2, qux: { baz: 1 } }
  test: obj == 42

plans = {
  'free-plan': #673,
  'freelancer': #669,
  'small-business': #668,
  'professional-business': #667,
  'enterprise': #666
}

body
  for plan in free-plan freelancer small-business professional-business enterprise
    test: plans[plan]
    plans[plan] = #ccc
  test: plans

obj = {}
obj.list = 1, 2, 3

body
  test: obj.list[0]
  obj['list'] = 4, 5, 6
  test: obj.list[0..2]
"""

    source = """
obj1 = {}
obj2 = { foo: 1, bar: 2 }

body
  test: obj1 == obj2
  test: obj2 != obj1
  test: obj1 == {}
  test: obj2 == { foo: 1, bar: 2 }

  obj2.qux = { baz: 1 }
  test: obj2 == { foo: 1, bar: 2, qux: { baz: 1 } }
  test: obj == 42
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
