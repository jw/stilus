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
.math
  test1: ceil(0.5)
  test2: floor(0.5)
  test3: round(0.5)
.math_units
  test1: ceil(0.5px)
  test2: floor(0.5px)
  test3: round(0.5px)
.math_precision0
  test1: ceil(0.47,0)
  test2: floor(0.47,0)
  test3: round(0.47,0)
.math_precision1
  test1: ceil(0.47,1)
  test2: floor(0.47,1)
  test3: round(0.47,1)
.math_precision2
  test1: ceil(0.472,2)
  test2: floor(0.472,2)
  test3: round(0.472,2)

.math_PI
  foo: PI

.math_sin
  test1: sin(0)
  test2: sin(30deg)
  test3: sin(45deg)
  test4: sin(60deg)
  test5: sin(90deg)
  test6: sin(180deg)
  test7: sin(270deg)
  test8: sin(360deg)

.math_cos
  test1: cos(0)
  test2: cos(30deg)
  test3: cos(45deg)
  test4: cos(60deg)
  test5: cos(90deg)
  test6: cos(180deg)
  test7: cos(270deg)
  test8: cos(360deg)

.math_tan
  test1: tan(0)
  test2: tan(30deg)
  test3: tan(45deg)
  test4: tan(60deg)
  test5: tan(90deg)
  test6: tan(180deg)
  test7: tan(270deg)
  test8: tan(360deg)

.math_sin_rad
  test1: sin(2*PI/3)
  test2: sin(3*PI/4)
  test3: sin(5*PI/6)
  test4: sin(7*PI/6)
  test5: sin(5*PI/4)
  test6: sin(4*PI/3)
  test7: sin(5*PI/3)
  test8: sin(7*PI/4)
  test9: sin(11*PI/6)
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
