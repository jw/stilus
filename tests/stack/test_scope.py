from stilus.nodes.null import null
from stilus.nodes.boolean import true
from stilus.nodes.ident import Ident
from stilus.stack.scope import Scope


def test_scope():
    scope = Scope()
    assert scope.locals == {}


def test_scope_lookup():
    scope = Scope()
    scope.add(Ident('one', 1))
    scope.add(Ident('two'))
    scope.add(Ident('three', true))
    assert len(scope.locals) == 3
    assert scope.lookup('one') == 1
    assert scope.lookup('two') == null
    assert scope.lookup('three') == true
    assert scope.lookup('four') is None
