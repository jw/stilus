from stilus.utils import assert_string
from stilus.visitor.normalizer import Normalizer


def selector_exists(selector, evaluator=None):
    assert_string(selector, 'selector')

    visitor = Normalizer(evaluator.root.clone(),
                         evaluator.parser,
                         evaluator.options)
    visitor.visit(visitor.root)

    return selector.string in visitor.selector_map
