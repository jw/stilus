from stilus.functions.component import component
from stilus.functions.hsla import hsla
from stilus.nodes.color import Color
from stilus.nodes.string import String
from stilus.nodes.unit import Unit


def lightness(color: Color, value=None, evaluator=None):
    if value:
        hsla_color = color.hsla()
        return hsla(Unit(hsla_color.hue),
                    Unit(hsla_color.saturation),
                    value,
                    Unit(hsla_color.a),
                    evaluator)
    return component(color, String('lightness'), evaluator)
