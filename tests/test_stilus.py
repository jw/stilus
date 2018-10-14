from stilus import stilus


def test_stylus():
    assert stilus.render('str', 'options') is None
