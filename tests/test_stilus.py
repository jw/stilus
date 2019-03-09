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
@keyframes foo
{
  from
  {
    color: red;
  }
  to
  {
    color: blue;
  }
}
"""

#     source = """// Last line in this file has 4 spaces.
# .myclass
#   display block
#   color black
#     """
    css = stilus.render(source, {})
    print(f'[{css.strip()}]')
