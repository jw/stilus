from stilus import stilus


def test_stylus():
    first_compile = 'abc {\n  color: red\n}\n'
    assert stilus.render('abc\n  color: red\n', {}) == first_compile
