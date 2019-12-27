from stilus.functions.blend import blend
from stilus.functions.luminosity import luminosity
from stilus.nodes.color import RGBA, Color
from stilus.nodes.literal import Literal
from stilus.nodes.null import Null
from stilus.nodes.object_node import ObjectNode
from stilus.nodes.unit import Unit
from stilus.utils import assert_color, stilus_round


def contrast(top: Color = None, bottom: Color = None, evaluator=None):
    if not isinstance(top, Color) and not isinstance(bottom, Color):
        c = '' if isinstance(top, Null) else f'{top}'
        return Literal(f'contrast({c})')
    result = ObjectNode()
    if not bottom:
        bottom = RGBA(255, 255, 255, 1)
    assert_color(bottom)
    bottom = bottom.rgba()

    def contrast_function(top, bottom):
        if 1 > top.a:
            top = blend(top, bottom)
        l1 = luminosity(bottom).value + 0.05
        l2 = luminosity(top).value + 0.05
        ratio = l1 / l2

        if l2 > l1:
            ratio = 1 / ratio

        return round(ratio * 10) / 10

    if 1 <= bottom.a:
        result_ratio = Unit(contrast_function(top, bottom))
        result.set('ratio', result_ratio)
        result.set('error', Unit(0))
        result.set('min', result_ratio)
        result.set('max', result_ratio)
    else:
        on_black = contrast_function(top,
                                     blend(bottom, RGBA(0, 0, 0, 1)))
        on_white = contrast_function(top,
                                     blend(bottom, RGBA(255, 255, 255, 1)))
        the_max = max(on_black, on_white)

        def process_channel(top_channel, bottm_channel):
            return min(max(0,
                           (top_channel - bottm_channel * bottom.a) /
                           (1 - bottom.a)),
                       255)

        closest = RGBA(process_channel(top.r, bottom.r),
                       process_channel(top.g, bottom.g),
                       process_channel(top.b, bottom.b),
                       1)

        the_min = contrast_function(top, blend(bottom, closest))

        result.set('ratio',
                   Unit(stilus_round((the_min + the_max) * 50) / 100))
        result.set('error',
                   Unit(stilus_round((the_max - the_min) * 50) / 100))
        result.set('min', Unit(the_min))
        result.set('max', Unit(the_max))

    return result
