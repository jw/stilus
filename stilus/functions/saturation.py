from stilus.functions.component import component
from stilus.functions.hsla import hsla
from stilus.nodes.string import String
from stilus.nodes.unit import Unit


def saturation(color, value):
    if value:
        hsla_color = color.hsla
        return hsla(Unit(hsla_color.h),
                    value,
                    Unit(hsla_color.l),
                    Unit(hsla_color.a))
    return component(color, String('saturation'))