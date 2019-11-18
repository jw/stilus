from nodes.null import null
from nodes.literal import Literal
from utils import unwrap, assert_string
from visitor.compiler import Compiler


def s(fmt, *args, evaluator=None):
    options = evaluator.options if evaluator else {}
    fmt = unwrap(fmt).nodes[0]
    assert_string(fmt, 'string')
    result = fmt.string
    for arg in args:
        from visitor.evaluator import Evaluator
        if not isinstance(arg, Evaluator):
            c = Compiler(arg, options).compile()
            result = result.replace('%s', str(c), 1)
    # add nulls for missed %s elements
    c = Compiler(null, options).compile()
    result = result.replace('%s', c)
    return Literal(result)
