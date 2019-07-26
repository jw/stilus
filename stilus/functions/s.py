from stilus.nodes.null import null
from stilus.nodes.literal import Literal
from stilus.utils import unwrap, assert_string
from stilus.visitor.compiler import Compiler


def s(fmt, *args):
    fmt = unwrap(fmt).nodes[0]
    assert_string(fmt, 'string')
    result = fmt.string
    for arg in args:
        # todo: use proper options (coming from the evaluator)
        c = Compiler(arg, {}).compile()
        result = result.replace('%s', c, 1)
    # add nulls for missed %s elements
    c = Compiler(null, {}).compile()
    result = result.replace('%s', c)
    return Literal(result)
