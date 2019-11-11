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

/*
 * Reset button related properties so that
 * a, button, and input's are supported.
 */

-reset()
  display: block;
  text-decoration: none;

/*
 * Minimalistic flat button with white inset.
 */

minimal-button(bg = #e3e3e3, intensity = 1)
  -reset()
  background: bg;
  border: 1px solid darken(bg, 15 * intensity);
  border-radius: 3px;
  box-shadow: inset 0 0 1px 1px rgba(white, 0.8 * intensity);
  color: #333;
  font-family: 'helvetica neue', helvetica, arial, sans-serif;
  font-size: 12px;
  font-weight: bold;
  line-height: 1;
  padding: 8px 0 9px;
  text-align: center;
  text-shadow: 0 1px 0 rgba(white, 1 * intensity);
  width: 150px;

  &:hover {
    background: darken(bg, 3);
    box-shadow: inset 0 0 1px 1px rgba(white, 0.5 * intensity);
    color: #222;
    cursor: pointer;
  }

  &:active {
    background: darken(bg, 5);
    box-shadow: inset 0 0 1px 1px rgba(white, 0.2 * intensity);
    color: #000;
  }

button,
a.button {
  minimal-button();
}
"""

    source = """
.popup
  box-shadow:
    0 -2px 2px            hsl(220, 20%, 40%),
    0 -10px 10px          hsl(220, 20%, 20%),
    0 0 15px              black,

    inset 0 5px 1px       hsla(220, 80%, 10%, 0.4), 
    inset 0 0 5px         hsla(220, 80%, 10%, 0.1),
    inset 0 20px 15px     hsla(220, 80%, 100%, 1),

    inset 0 1px 0         hsl(
                            219,
                            20%,
                            0%
                          ), 

    inset 0 1px 0         hsl(
                            219
                          , 20%
                          , 0%
                          ),

    inset 0 -50px 50px -40px hsla(220, 80%, 10%, .3),

    inset 0 -1px 0px      hsl(220, 20%, 20%),
    inset 0 -2px 0px      hsl(220, 20%, 40%),
    inset 0 -2px 1px      hsl(220, 20%, 65%), 
    inset 0 -3px 0px      hsl(220, 20%, 50%),
    inset 0 -4px 0px      hsl(220, 20%, 50%),
    inset 0 -5px 0px      hsl(220, 20%, 70%),
    inset 0 -5px 1px      hsl(220, 20%, 50%), 
    inset 0 -6px 0px      hsl(220, 20%, 60%),
    inset 0 -7px 0px      hsl(220, 20%, 60%),
    inset 0 -8px 0px      hsl(220, 20%, 80%),
    inset 0 -8px 1px      hsl(220, 20%, 70%), 
    inset 0 -9px 0px      hsl(220, 20%, 100%),

    inset 0 -20px 20px    hsla(220, 80%, 10%, 0.15),

    inset 25px 20px 15px  hsla(220, 20%, 40%, 0.1),
    inset 50px 20px 50px  hsla(220, 20%, 40%, 0.1)
  foo: 'bar'

families = Helvetica,
  Arial,
  sans-serif

body
  font-families: families

a = {}

bar(obj, bool)
  obj.params = { foo: 'bar' }

baz(params)
  body
    foo: params.foo

foo()
  if true
    bar(a,
      true)

  baz(a.params)

foo()
"""

    source = """
vendors = webkit

@keyframes colors
  0%
    background-color red
  15%
    background-color blue
  100%
    background-color black
"""

    # parser = Parser(source, {})
    # ast = parser.parse()
    # print(f'{ast}')

    stylus_path = '/home/jw/python/projects/stilus/tests/stylus'
    renderer = Renderer(source, {})
    renderer.include(f'{stylus_path}/images')
    renderer.include(f'{stylus_path}/cases')
    renderer.include(f'{stylus_path}/cases/import.basic')
    renderer.include('.')

    # renderer.options['include css'] = True
    # renderer.options['compress'] = True

    css = renderer.render()

    print(f'------------- result ---\n'
          f'{css}'
          f'------------------------')
