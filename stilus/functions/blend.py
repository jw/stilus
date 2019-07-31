from stilus.nodes.color import RGBA
from stilus.utils import assert_color


def blend(top, bottom=None, evaluator=None):
    assert_color(top)
    top = top.rgba()
    if not bottom:
        bottom = RGBA(255, 255, 255, 1)
    assert_color(bottom)
    bottom = bottom.rgba()

    return RGBA(top.r * top.a + bottom.r * (1 - top.a),
                top.g * top.a + bottom.g * (1 - top.a),
                top.b * top.a + bottom.b * (1 - top.a),
                top.a + bottom.a - top.a * bottom.a)
