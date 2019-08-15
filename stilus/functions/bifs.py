# todo: clean these up
from stilus.functions import replace, listSeparator, currentMedia
from stilus.functions import baseConvert, s
from stilus.functions import hue, lightness, saturation
from stilus.functions import hsl, rgb, alpha, blue, green, red
from stilus.functions import rgba, hsla, contrast, luminosity
from stilus.functions import adjust, math, math_prop, unit, length, \
    addProperty, unquote, clone, lookup, basename, blend, convert, \
    type_function, push

bifs = {
    '-math-prop': math_prop.math_prop,
    'add-property': addProperty.addProperty,
    'adjust': adjust.adjust,
    'alpha': alpha.alpha,
    'base-convert': baseConvert.baseConvert,
    'basename': basename.basename,
    'blend': blend.blend,
    'blue': blue.blue,
    'clone': clone.clone,
    'convert': convert.convert,
    'contrast': contrast.contrast,
    'current-media': currentMedia.currentMedia,
    'green': green.green,
    'hsl': hsl.hsl,
    'hsla': hsla.hsla,
    'hue': hue.hue,
    'length': length.length,
    'lightness': lightness.lightness,
    'list-separator': listSeparator.listSeparator,
    'luminosity': luminosity.luminosity,
    'lookup': lookup.lookup,
    'math': math.math,
    'push': push.push,
    'red': red.red,
    'replace': replace.replace,
    'rgb': rgb.rgb,
    'rgba': rgba.rgba,
    's': s.s,
    'saturation': saturation.saturation,
    'type': type_function.type_function,
    'unit': unit.unit,
    'unquote': unquote.unquote,
}

raw_bifs = ['addProperty', 'baseConvert', 'clone', 'length',
            'listSeparator', 'push', 's']
