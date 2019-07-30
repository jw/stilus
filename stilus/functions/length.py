from stilus import utils


# todo: the *args is there due to javascript weirdness.
def length(expr, *args, evaluator=None):
    if expr:
        if expr.nodes:
            nodes = utils.unwrap(expr).nodes
            if len(nodes) == 1 and nodes[0].node_name == 'object':
                return len(nodes[0])
            else:
                return len(nodes)
        else:
            return 1
    return 0
