from functions.component import component
from functions.hsla import hsla
from nodes.color import Color
from nodes.string import String
from nodes.unit import Unit


def hue(color: Color, value=None, evaluator=None):
    if value:
        hsla_color = color.hsla()
        return hsla(value,
                    Unit(hsla_color.saturation),
                    Unit(hsla_color.lightness),
                    Unit(hsla_color.a),
                    evaluator)
    return component(color, String('hue'))
