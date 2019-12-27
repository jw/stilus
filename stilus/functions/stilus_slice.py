from stilus import utils
from stilus.nodes.ident import Ident
from stilus.nodes.string import String


def slice(values, start, end=None, evaluator=None):
    start = int(start.nodes[0].value)
    if end and len(end.nodes) > 0:
        end = int(end.nodes[0].value)

    values = utils.unwrap(values).nodes

    if len(values) > 1:
        if end:
            return utils.coerce(values[start:end], raw=True)
        else:
            return utils.coerce(values[start:], raw=True)

    if end:
        result = values[0].string[start:end]
    else:
        result = values[0].string[start:]

    if isinstance(values[0], Ident):
        return Ident(result)
    else:
        return String(result)
