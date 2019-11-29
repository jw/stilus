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
body
 bar{color:'asdf'}

"""

    source = """
@font-face
  font-family: "Your typeface"
  src: url("type/filename.eot")

@font-face
    font-family 'SPEdessa'
    src: url('fonts/spedessa-webfont.eot')
    src: url('fonts/spedessa-webfont.eot?#iefix') format('embedded-opentype'),
         url('fonts/spedessa-webfont.woff') format('woff'),
         url('fonts/spedessa-webfont.ttf') format('truetype')
    font-weight: normal
    font-style: normal

@font-face
{
  font-family: 'ekibastuzregular'
}

"""

    source = """

padding(n)
  padding n

body
  padding(5px)
  padding(5px 10px)

padding(y, x = null)
  padding y x

body
  padding(5px)
  padding(5px, 10px)

padding(args...)
  padding args

body
  padding(5px)
  padding(5px, 10px)
  padding(5px, 10px, 0 2px)

padding(y, rest...)
  test-y y
  if rest
    padding rest

body
  padding(1px)
  padding(1px, 2px, 3px)

padding(args...)
  if args
    test-y args[0]
    test-x args[1]

body
  padding(1px)
  padding(1px, 2px)
"""

    new_source = """
add(a, b)
  a + b

pad(x, y)
  padding y x y x

body
  pad(5px, 10px)

form .button
  padding-left add(10px, 5px)

-opposite-position(pos)
  if pos == top
    bottom
  else if pos == bottom
    top
  else if pos == left
    right
  else if pos == right
    left
  else
    error('Invalid position ' + pos)

opposite(positions)
  for pos in positions
    pos = -opposite-position(pos)
    ret = ret is defined ? ret pos : pos

body
  foo opposite(top)
  foo opposite(left)
  foo opposite(top left)
"""

    source = """

body
  padding 5px

body
 padding 5px

body
  padding: 5px;  margin: 0;

body
    padding: 5px;
    margin: 0;

body {
     padding: 5px;
  margin: 0;
}

body {
  padding: 5px;  margin: 0;
}

body {
padding: 5px;
}

ul {
  li {
    padding: 5px;
}
}


body{padding: 5px;}
foo
 bar {color:'asdf'}
 bar{color:'asdf'}
"""

    source = """

body
  padding 5px

body
 padding 5px

body
  padding: 5px;  margin: 0;

body
    padding: 5px;
    margin: 0;

body {
     padding: 5px;
  margin: 0;
}

body {
  padding: 5px;  margin: 0;
}

body {
padding: 5px;
}

ul {
  li {
    padding: 5px;
}
}


body{padding: 5px;}
foo
 bar {color:'asdf'}
 bar{color:'asdf'}
"""

    source = """
icons = json('import.json/icons.json', { hash: true, leave-strings: true });

.icon
  content: icons.menu
"""

    source = """
pad-y(top, bottom) {
  padding-top: top;
  padding-bottom: bottom;
}

#login {
  pad-y(15px, 100px);
}

#login {
  pad-y(bottom: 100px, top: 15px);
}

#login {
  pad-y(top: 15px, bottom: 100px);
}

#login {
  pad-y(bottom: 100px, 15px);
}

#login {
  pad-y(15px, bottom: 100px);
}

#login {
  pad-y(100px, top: 15px);
}

#login {
  pad-y(top: 15px, 100px);
}

#login {
  pad-y(15px, bottom: 100px);
}

#login {
  foo: operate('/', 2, 10);
  foo: operate('/', 10, 2);

  foo: operate(op: '/', 10, 2);
  foo: operate(10, op: '/', 2);
  foo: operate(10, 2, op: '/');

  foo: operate('/', left: 10, right: 2);
  foo: operate('/', right: 2, left: 10);
  foo: operate(right: 2, left: 10, op: '/');

  foo: operate(right: 10, left: 2, op: '/');
  foo: operate('/', left: 2, right: 10);
}

body {
  foo: join(', ', 1, 2, 3);
  foo: join(', ', 1 2 3);
  foo: join(delim: ', ', 1, 2, 3);
  foo: join(1, 2, 3, delim: '|');
  foo: join(1, delim: '|', 2, 3);
}

body {
  foo: join('|', 1, 2, 3);
  foo: join(1 2 3, delim: '|');
  foo: join(delim: '|', 1 2 3);
}
"""

    source_foo = """
body
  foo join(' ', 1 2 3)
  foo join(', ', 1 2 3)
  foo join(',', 1 2 3)
  foo join(',', 1)
  foo join(',') == null

body
  foo join(', ', 1, 2, 3)
  foo join(', ', one 1, two 2, three 3)

body
  a = 1 2
  b = 3 4
  c = 5 6
  foo: join(', ', 1 2, #fff #000, 5px 6px)
  foo: join(', ', a, b, c)
  foo: join(', ', a b c)
  foo: join(', ', 1, 2, 3, 4, 5, 6)
  foo: join(', ', 1 2 3 4 5 6)
  foo: join(', ', hsl(0, 0%, 0%), hsl(120, 20%, 80%))
  foo: join(', ', hsla(120, 20%, 80%, 1), hsla(90, 0%, 0%, 1))
"""

    source = """
@charset 'utf-8'

@namespace svg url(http://www.w3.org/2000/svg)

body
  background-color red

svg|svg
  fill blue

svg|.foo
  fill green

svg|.bar
  fill yellow
"""

    source = """
.embed-no-hash {
  color: #c00;
  background: embedurl("circle.svg");
}

.embed-with-hash {
  color: #c00;
  background: embedurl("circle.svg#some-id");
}

.embed-with-utf8 {
  color: #c00;
  background: embedurl("circle.svg", "utf8");
}

.too-big-no-hash {
  color: #c00;
  background: url("tiger.svg");
}

.too-big-with-hash {
  color: #c00;
  background: url("tiger.svg#some-id");
}
"""

    source = """

pad(types = margin padding, n = 5px)
  padding unit(n, px) if padding in types
  margin unit(n, px) if margin in types

body
  pad()

body
  pad(margin)

body
  apply-mixins = true
  pad(padding, 10) if apply-mixins

body
  foo pad()
"""

    sourced = """

get-red()
  p('in red')
  red

set-colour(colour = get-red)
  p('in colour')
  color colour()

.red
  set-colour()
"""

    source = """
@keyframes tada
  0%
    transform: scale(1)
  10%, 20%
    transform: scale(.9) rotate(-3deg)
  from, to
    background: scale(.5)
"""

    source = """
only = webkit

body
  foo: webkit in only
  foo: (webkit in only)
  foo: true or false
  foo: (webkit in only) or false
"""

    source = """
a
  a: foo bar(baz, buz, 1)
  b: '' + @a
  c: join(' ', @a)
"""
    source = """
@import url("import.include.resolver.css-file/a.css");
// @import "import.include.resolver.images/a"
"""

    source = """
body
  // 5px
  foo 0 || 5px

  // 0px
  foo 0px || 5px

  // 0px
  foo 0px || 0px

  // false
  foo 0 or false

  // true
  foo 0 || 0 || true

  // 5px
  foo 1px && 5px

  // 1px
  foo 0px && 1px

  // 0
  foo 1px && 0

  // false
  foo 1px and false

  // 10
  foo 5px && 5px && 10

  // #fff
  foo #000 && #fff

  // 1
  foo 8 && (4 && 1)

  // true
  type = "color"
  foo #fff is a type
  foo #fff is a 'color'

  // false
  foo 15px is a 'color'
  // true
  foo 15px is a 'unit'

  // true
  foo 15px is a 'unit' and #fff is a 'color'

  // true
  foo = 'bar'

  // true
  bar = 'baz'
  foo foo is defined and bar is defined

  // false
  foo baz is defined

  // wahoo
  foo bar is defined ? wahoo : nope

  // nope
  foo rawr is defined ? yes : nope

  // "got 15px"
  foo "got " + 15px

  // 1
  foo true and 1 or 5

  // 5
  foo !false and !false and 5

  // true
  foo !!5 is true or !!0 is false
  foo !!5 == false or !!0 == false

  // true
  foo wahoo == wahoo

  // false
  foo 0 == true
  foo true == 0
  foo #fff == undefined


body
  nums = 1 2
  foo: '<%s:%s>' % 12
  foo: '<%s:%s>' % nums
  foo: '<a: %s b: %s>' % 1 2 // not what you might think
  foo: '<a: %s b: %s>' % (1 2)
  foo: 'X::Micrsoft::crap(%s)' % rgb(0,255,0)
  foo: '<%s, %s, %s>' % (foo bar baz)

body
  foo 5 < '5.1'
  foo 5 < 5.1
  foo 5 <= 5.1
  foo !(5 < '5')
  foo 5.1 > 5
  foo !(5 > 5)
  foo '5.1' > 5
  foo '5.1' > '5'
  foo (5 - "5.1") != 0
  foo !(5 == '5.1')

str = ''

body
  str += 'bar'
  foo: str

body
  foo = 40em
  bar = '40em'
  width type(foo) == 'unit' && unit(foo)
  height type(bar) == 'unit' && unit(bar)
"""

    source = """
body
  // 4
  foo (--- 0) or 4
  // 4
  foo --- 0 or 4
  // -5px
  foo ---5px
  // 2
  foo (!!!5) or 2
  foo !!!5 or 2


body
  // true
  foo !(! 5)
  foo !!5

body
  // 5
  foo (! false) and (! false) and 5
  foo ! false and ! false and 5

body
  // true
  foo (!!5 == true) or (!!0 == false)
  foo !!5 == true or !!0 == false
  foo (!!5 == false) or (!!0 == false)
  foo !!5 == false or !!0 == false
  // 2
  foo 5 < 10 and !!5 and 2

body
  // true
  foo (!!true) and (!!true)
  foo !!true and !!true

body
  test()
    5 * 2 - 15 / 2
  // 2.5
  foo test()
  foo (5 * 2) - (15 / 2)

body
  // true
  foo not 5 < 10 ? 0 : 1
  // true
  foo !(5 < 10 ? 0 : 1)
  // false
  foo !(5 > 10 ? 0 : 1)
  // wahoo
  foo !! 1 ? wahoo : fail
  // fail
  foo !1 ? wahoo : fail

body
  foo = 'test'
  bar = 'test'
  // true
  foo (foo is defined) and (bar is defined)
  foo foo is defined and bar is defined

body
  // true
  foo 5 > 4 is a 'boolean'

  foo = type is a 'unit' ? type : 1
  // 1
  foo foo

body
  padding = false
  margin = false

  // true
  foo !padding or !margin
  foo not padding or margin

  // false
  foo not padding or margin == !padding or !margin
  // true
  foo (not padding or margin) == !padding or !margin
"""

    source = """
html {font-size:100.01%;}
"""

    source = """
another()
  foo bar
  bar baz
  return
  baz raz

body
  another()
"""

    source = """
body
  foo 1 == 1
  foo '1' == 1  // oops
  foo 1 == '1'
  foo 1 == '5' == false
  foo 5 == 1 == false
  foo 5 != 1
  foo 5 != asdf
  foo 5 == asdf == false
  foo !(5 == '5.1')
  foo 5 != '5.1'
  foo '5' != '5.1'

body
  foo 1000ms == 1s
  foo 1s == 1000ms
  foo 1s == 500ms == false

body
  foo wahoo == wahoo
  foo wahoo == 'wahoo'
  foo wahoo == unquote('wahoo')

body
  foo unquote('wahoo') == wahoo
"""
    """
  foo 'wahoo' == wahoo

body
  something = 'yay'
  foo yes == (something is defined ? yes : nope)
  foo nope == (whatever is defined ? yes : nope)

body
  foo: (1 2 3) == (1 2 3)
  foo: (foo bar baz) == (foo bar baz)
  foo: () == ()

body
  foo: (foo bar baz) == (foo hey baz)
  foo: (1 2 3) == (1 2 0)
  foo: (1) == (1 2 3)
  foo: (2 2) == (2)
  foo: (2 2) == ()
  foo: () == true
  foo: true == ()
  foo: !!()

body
  foo: (1 2 3) != (1 1 3)
  foo: (foo bar baz) != (foo 1 2)
  foo: () != (1)
  foo: (1) != (0)
  foo: () != (null)

body
  foo: (1 2 3) != (1 2 3)
  foo: (foo bar) != (foo bar)
  foo: () != ()
"""

    source = """
textarea, input
  border 1px solid #eee
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
