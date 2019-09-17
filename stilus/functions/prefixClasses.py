from stilus.utils import assert_string, assert_type


def prefix_classes(prefix, block=None, evaluator=None):
    assert_string(prefix, 'prefix')
    assert_type(block, 'block', 'block')

    _prefix = evaluator.prefix

    evaluator.options['prefix'] = evaluator.prefix = prefix.string
    block = evaluator.visit(block)
    evaluator.options['prefix'] = evaluator.prefix = _prefix
    return block
