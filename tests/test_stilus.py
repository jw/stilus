from stilus import stilus


def test_stylus():
    # css = 'abc {\n  color: red\n}\n'
    assert None is stilus.render('abc\n  color: red\n', {})


if __name__ == '__main__':
    first_compile = 'abc\n  color: red\n'
    print(f'result: {stilus.render(first_compile, {})}')
