from stilus import utils
from stilus.exceptions import StilusError
from stilus.nodes.literal import Literal


def opposite_position(positions, evaluator=None):
    expr = []
    nodes = utils.unwrap(positions)
    for i, node in enumerate(nodes):
        utils.assert_string(node, f"position {i}")
        if node.string == "top":
            expr.append(Literal("bottom"))
        elif node.string == "bottom":
            expr.append(Literal("top"))
        elif node.string == "left":
            expr.append(Literal("right"))
        elif node.string == "right":
            expr.append(Literal("left"))
        elif node.string == "center":
            expr.append(Literal("center"))
        else:
            raise StilusError(f"invalid position {i}")
    return expr
