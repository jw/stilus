from stilus.nodes.color import Color
from stilus.nodes.unit import Unit
from stilus.utils import assert_color


def luminosity(color: Color, evaluator=None):
    assert_color(color)
    color = color.rgba()

    def process_channel(channel):
        channel = channel / 255
        if 0.03928 > channel:
            return channel / 12.92
        else:
            return pow((channel + 0.055) / 1.055, 2.4)

    return Unit(0.2126 * process_channel(color.r) +
                0.7152 * process_channel(color.g) +
                0.0722 * process_channel(color.b))
