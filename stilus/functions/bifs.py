from stilus.functions import addProperty, adjust, alpha, baseConvert, \
    basename, blend, blue, clone, contrast, convert, currentMedia, green, \
    hsl, hsla, hue, length, lightness, listSeparator, lookup, luminosity, \
    math, math_prop, push, red, replace, rgb, rgba, s, saturation, \
    type_function, unit, unquote

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
