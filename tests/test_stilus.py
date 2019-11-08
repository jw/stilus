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

mixin()
  td:nth-of-type(2)
  td:nth-of-type(3)
    background black

ul
  mixin()

table
  td:nth-child(2)
  td:nth-child(3)
  td:nth-child(4)
  td:nth-child(5)
  td:first-letter
    background black
    li:first-child
    li:last-child
      background white

table
  :nth-child(2)
  :nth-child(3)
    background black

table
  td:after, td .after
    background red
  td
    background white

table
  td:before, td::before
    color green
  td:selection, td::selection
    color red
  td:first-line
    color yellow
  td::first-letter
    color black

label
  input:indeterminate
  span
    color #001
  input:checked
  span
    color #002
  a:any-link
  span
    color #003
  a:local-link
  span
    color #004
  input:read-only
  span
    color #005
  input:read-write
  span
    color #006
  input:placeholder-shown
  span
    color #007
  // input:default
  // span
  //   color #008
  //  throws illegal unary "in", missing left-hand operand
  // input:in-range
  // span
  //   color #009
  input:out-of-range
  span
    color #010
  input:required
  span
    color #011
  input:optional
  span
    color #012
  input:user-error
  span
    color #013
  input:blank
  span
    color #014
"""

    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(f'{ast}')

    renderer = Renderer(source, {})
    # renderer.options['include css'] = True
    renderer.include('/home/jw/python/projects/stilus/tests/stylus/images')
    renderer.include('/home/jw/python/projects/stilus/tests/stylus/cases')
    renderer.include('/home/jw/python/projects/stilus/tests/stylus/'
                     'cases/import.basic')
    renderer.include('.')
    # renderer.options['compress'] = True

    css = renderer.render()

    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')
