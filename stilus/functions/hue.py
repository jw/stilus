from stilus.functions.hsla import hsla
from stilus.nodes.unit import Unit


def hue(color, value):
    if value:
        hsla_color = color.hsla
        return hsla(value,
                    Unit(hsla_color.s),
                    Unit(hsla_color.l),
                    Unit(hsla_color.a))
    return Component(color, String('hue'))