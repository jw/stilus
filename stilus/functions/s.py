from stilus.nodes.null import null
from stilus.nodes.literal import Literal
from stilus.utils import unwrap, assert_string
from stilus.visitor.compiler import Compiler


def s(fmt, *args, evaluator=None):
    options = evaluator.options if evaluator else {}
    fmt = unwrap(fmt).nodes[0]
    assert_string(fmt, 'string')
    result = fmt.string
    for arg in args:
        from stilus.visitor.evaluator import Evaluator
        if not isinstance(arg, Evaluator):
            c = Compiler(arg, options).compile()
            result = result.replace('%s', c, 1)
    # add nulls for missed %s elements
    c = Compiler(null, options).compile()
    result = result.replace('%s', c)
    return Literal(result)
