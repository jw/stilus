from stilus.functions import hue, lightness, saturation
from stilus.functions import hsl, rgb, alpha, blue, green, red
from stilus.functions import rgba, hsla
from stilus.functions import adjust, math, math_prop, unit, length, \
    addProperty, unquote

bifs = {
    '-math-prop': math_prop.math_prop,
    'addProperty': addProperty.addProperty,
    'adjust': adjust.adjust,
    'alpha': alpha.alpha,
    'blue': blue.blue,
    'green': green.green,
    'hsl': hsl.hsl,
    'hsla': hsla.hsla,
    'hue': hue.hue,
    'length': length.length,
    'lightness': lightness.lightness,
    'math': math.math,
    'red': red.red,
    'rgb': rgb.rgb,
    'rgba': rgba.rgba,
    'saturation': saturation.saturation,
    'unit': unit.unit,
    'unquote': unquote.unquote,
}

raw_bifs = ['addProperty', 'length']
