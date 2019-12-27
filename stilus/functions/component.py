from stilus.nodes.color import Color
from stilus.utils import assert_color, assert_string
from stilus.nodes.unit import Unit

component_map = {
    'red': 'r',
    'green': 'g',
    'blue': 'b',
    'alpha': 'alpha',
    'hue': 'hue',
    'saturation': 'saturation',
    'lightness': 'lightness'
}

unit_map = {
    'hue': 'deg',
    'saturation': '%',
    'lightness': '%'
}

type_map = {
    'red': 'rgba',
    'green': 'rgba',
    'blue': 'rgba',
    'alpha': 'rgba',
    'hue': 'hsla',
    'saturation': 'hsla',
    'lightness': 'hsla'
}


def component(color: Color, name: str, evaluator=None) -> Unit:
    """Return component `name` for a given `color`.
    :param color: Color
    :param name: str
    :return: Unit
    """
    assert_color(color, 'color')
    assert_string(name, 'name')
    name = name.string
    unit = unit_map.setdefault(name, None)
    type = type_map[name]
    name = component_map[name]
    try:
        return Unit(getattr(getattr(color, type)(), name), unit)
    except AttributeError:
        raise TypeError(f'invalid color component "{name}"')
