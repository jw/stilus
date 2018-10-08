from stilus.utils import assert_color, assert_string
from stilus.nodes.unit import Unit

component_map = {
    'red': 'r',
    'green': 'g',
    'blue': 'b',
    'alpha': 'a',
    'hue': 'h',
    'saturation': 's',
    'lightness': 'l'
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


def component(color, name):
    assert_color(color, 'color')
    assert_string(name, 'name')
    name = name.string
    unit = unit_map[name]
    type = type_map[name]
    name = component_map[name]
    if not name:
        raise TypeError(f'invalid color component "{name}"')
    return Unit(color[type][name], unit)
