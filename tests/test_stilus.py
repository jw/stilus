from stilus import stilus
from stilus.stilus import Renderer


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
@foo
  $bar
    color: red
// @foo bar baz;
.bar
  @extend $bar
"""

    source = """
$bar
  color: red
.bar
  @extend $bar
"""

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
json('import.json/vars.json')

@media queries-small
  body
    //string variable
    display nope
    //color calc
    color darken(color, 50%)
    //color calc rgb(a)
    background-color: darken(background-color, 50%)
    border-color: fade-color
    //color calc alias (i.e. "purple")
    outline-color: darken(bg, 50%)
    //number variable
    padding spacing
    //acts the same as regular variables
    outline 1.5 * spacing
    margin gutter * 2
    if awesome
      border red
    //rgba with single digit values
    text-decoration-color decoration-color
    text-shadow 0 1px shadow-color

//nested json variable
@media queries-large
  body
    //deep nested json variable
    -webkit-transition animate-special-out

.a
  prefix = '$'
  json('import.json/local-vars.json', true, prefix)
  color $params-color
  width 10px * $a
  height 10px * $b
  background $bg

.b
  color $params-color
  background-color alternate-color

vars = json('import.json/vars.json', { hash: true });

body
  display: vars.nope
  color: darken(vars.color, 50%)
  background-color: darken(vars.background-color, 50%)
  border-color: vars.fade-color
  outline-color: darken(vars.bg, 50%)
  padding: vars.spacing
  outline: 1.5 * vars.spacing
  margin: vars.gutter * 2
  -webkit-transition: vars.animate.special.out
  if vars.awesome
    border red

icons = json('import.json/icons.json', { hash: true, leave-strings: true });

.icon
  content: icons.menu

optional = json('import.json/optional.json', { hash: true, optional: true })

body
  test: typeof(optional) == 'null'

"""

    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(f'{ast}')

    renderer = Renderer(source, {})
    renderer.options['include css'] = True
    renderer.include('/home/jw/python/projects/stilus/tests/stylus/images')
    renderer.include('/home/jw/python/projects/stilus/tests/stylus/cases')
    renderer.include('/home/jw/python/projects/stilus/tests/stylus/'
                     'cases/import.basic')
    renderer.include('.')

    css = renderer.render()

    # debugger = Debugger(ast, {})
    # for i, d in enumerate(debugger.debug()):
    #     print(f'{i}: {d}')

    # cases = '/home/jw/python/projects/stilus/tests/stylus/cases/'
    # run_test_case(cases + 'bifs.json.styl',
    #               cases + 'bifs.json.css')
    #
    # print(f'------------------------')
    #
    # run_test_case(cases + 'vargs.call.styl',
    #               cases + 'vargs.call.css')

    # css = Renderer(source, {}).render()

    # css = stilus.render(source, {})

    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')
