from stilus import stilus


def test_stylus():
    source = 'abc\n  color: red\n'
    css = 'abc {\n  color: #f00;\n}\n'
    assert stilus.render(source, {}) == css


if __name__ == '__main__':
    source = '\nsize = 12px\n\nbody\n  font-size size\n\n'
    css = 'body {\n  front-size: 12px;\n}'
    assert stilus.render(source, {}) == css
