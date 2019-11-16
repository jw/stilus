from nodes.null import null
from nodes.boolean import true
from nodes.ident import Ident
from stack.scope import Scope


def test_scope():
    scope = Scope()
    assert scope.commons == {}
    assert scope.lookup('foo') is None
    # assert str(scope) == '[Scope]'


def test_scope_add():
    scope = Scope()
    scope.add(Ident('one', 1))
    assert scope.commons['one'] == 1
    scope.add(Ident(None, None))
    assert scope.commons[None] == null
    scope.add(Ident('two'))
    assert scope.commons['two'] == null
    assert str(scope) == '[Scope @one, @None, @two]'


def test_scope_lookup():
    scope = Scope()
    scope.add(Ident('one', 1))
    scope.add(Ident('two'))
    scope.add(Ident('three', true))
    assert len(scope.commons) == 3
    assert scope.lookup('one') == 1
    assert scope.lookup('two') == null
    assert scope.lookup('three') == true
    assert scope.lookup('four') is None
    assert scope.lookup(None) is None
    assert str(scope) == '[Scope @one, @two, @three]'
