from stilus.functions import rgba
from stilus.functions import adjust, blue, math, math_prop, unit, length, \
    addProperty, unquote

bifs = {
    '-math-prop': math_prop.math_prop,
    'addProperty': addProperty.addProperty,
    'adjust': adjust.adjust,
    'blue': blue.blue,
    'rgba': rgba.rgba,
    'length': length.length,
    'math': math.math,
    'unit': unit.unit,
    'unquote': unquote.unquote,
}

raw_bifs = ['addProperty', 'length']
