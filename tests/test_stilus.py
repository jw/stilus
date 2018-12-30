from stilus import stilus


def test_stylus():
    source = 'abc\n  color: red\n'
    css = 'abc {\n  color: #f00;\n}\n'
    assert stilus.render(source, {}) == css


if __name__ == '__main__':
    source = 'abc\n  color: transparent\n'
    css = 'abc {\n  color: transparent;\n}\n'
    assert stilus.render(source, {}) == css
