from stilus.nodes.color import RGBA
from stilus.nodes.unit import Unit
from stilus.utils import assert_color, assert_type


def best(top, bottom):
    divisor = 255 if 0 < top - bottom else 0
    return (top - bottom) / (divisor - bottom)


def best_alpha(top, bottom):
    values = []
    values.append(best(top.r, bottom.r))
    values.append(best(top.g, bottom.g))
    values.append(best(top.b, bottom.b))
    return max(values)


def transparentify(top, bottom=None, alpha=None, evaluator=None):
    if isinstance(bottom, Unit):
        # dirty hack
        alpha = bottom
        bottom = None
    assert_color(top)
    top = top.rgba()
    if not bottom:
        bottom = RGBA(255, 255, 255, 1)
    if not alpha and bottom and hasattr(bottom, 'rgba') and not bottom.rgba:
        alpha = bottom
        bottom = RGBA(255, 255, 255, 1)
    assert_color(bottom)
    bottom = bottom.rgba()

    ba = best_alpha(top, bottom)

    if alpha:
        assert_type(alpha, 'unit', 'aplha')
        if alpha.type == '%':
            ba = alpha.value / 100
        elif not alpha.type:
            ba = alpha = alpha.value

    ba = max(min(ba, 1), 0)

    if ba == 0:
        return RGBA(bottom.r, bottom.g, bottom.b, round(ba * 100) / 100)
    else:
        return RGBA(bottom.r + (top.r - bottom.r) / ba,
                    bottom.g + (top.g - bottom.g) / ba,
                    bottom.b + (top.b - bottom.b) / ba,
                    round(ba * 100) / 100)
