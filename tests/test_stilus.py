from stilus import stilus


def test_stylus():
    source = 'abc\n  color: red\n'
    # css = 'abc {\n  color: #f00\n}\n'
    assert stilus.render(source, {})
