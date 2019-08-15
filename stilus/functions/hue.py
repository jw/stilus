from stilus.functions.component import component
from stilus.functions.hsla import hsla
from stilus.nodes.color import Color
from stilus.nodes.string import String
from stilus.nodes.unit import Unit


def hue(color: Color, value=None, evaluator=None):
    if value:
        hsla_color = color.hsla()
        return hsla(value,
                    Unit(hsla_color.saturation),
                    Unit(hsla_color.lightness),
                    Unit(hsla_color.a),
                    evaluator)
    return component(color, String('hue'))
