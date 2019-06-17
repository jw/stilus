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
padding(y, rest...)
  test-y y
  if rest
    padding rest

body
  padding 1px 2px 3px
"""

#     source = """
# foo
#   hello
#
#   bar
#     there
#
#     fizz
#       abc
#
# fuzz
#   def
# """

    source = """
//padding(n)
//  padding n
//
//body
//  padding 5px
//  padding 5px 10px
//
//padding(y, x = null)
//  padding y x
//
//body
//  padding 5px
//  padding 5px 10px
//
//padding(args...)
//  padding args
//
//body
//  padding 5px
//  padding 5px 10px
//  padding 5px 10px 0 2px
//
padding(y, rest...)
  test-y y
  if rest
    padding rest

body
  padding 1px
  padding 1px 2px 3px
//
//padding(args...)
//  if args
//    test-y args[0]
//    test-x args[1]
//
//body
//  padding 1px
//  padding 1px 2px
//
//padding(args...)
//  pad args[0]
//  pad args[1]
//  pad args[2]
//  len length(args)
//
//body
//  padding 1 2 (3 4 5)
//
//foo(args...)
//  bar: args
//
//body
//  foo 1 2 3
//  foo 1, 2, 3
"""

    css = stilus.render(source, {})
    print(f'result:\n[{css}]')
