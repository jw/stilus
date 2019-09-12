from stilus.functions import addProperty, adjust, alpha, baseConvert, \
    basename, blend, blue, clone, contrast, convert, currentMedia, green, \
    hsl, hsla, hue, length, lightness, listSeparator, lookup, luminosity, \
    math, math_prop, push, red, replace, rgb, rgba, s, saturation, \
    type_function, unit, unquote

# new functions
from stilus.functions import error, extname, define, dirname, p, pop, shift, \
    unshift, imageSize, json


bifs = {
    '-math-prop': math_prop.math_prop,
    'add-property': addProperty.add_property,
    'adjust': adjust.adjust,
    'alpha': alpha.alpha,
    'append': push.push,
    'base-convert': baseConvert.base_convert,
    'basename': basename.basename,
    'blend': blend.blend,
    'blue': blue.blue,
    'clone': clone.clone,
    'convert': convert.convert,
    'contrast': contrast.contrast,
    'current-media': currentMedia.current_media,
    'define': define.define,
    'dirname': dirname.dirname,
    'error': error.error,
    'extname': extname.extname,
    'green': green.green,
    'hsl': hsl.hsl,
    'hsla': hsla.hsla,
    'hue': hue.hue,
    'image-size': imageSize.image_size,
    'json': json.json_function,
    'length': length.length,
    'lightness': lightness.lightness,
    'list-separator': listSeparator.list_separator,
    'luminosity': luminosity.luminosity,
    'lookup': lookup.lookup,
    'math': math.math,
    'p': p.p,
    'pop': pop.pop,
    'push': push.push,
    'prepend': unshift.unshift,
    'red': red.red,
    'replace': replace.replace,
    'rgb': rgb.rgb,
    'rgba': rgba.rgba,
    's': s.s,
    'saturation': saturation.saturation,
    'shift': shift.shift,
    'type': type_function.type_function,
    'typeof': type_function.type_function,
    'unit': unit.unit,
    'unquote': unquote.unquote,
    'unshift': unshift.unshift,
}

raw_bifs = ['add_property', 'append', 'base_convert', 'clone', 'length',
            'list_separator', 'p', 'pop', 'push', 'prepend', 's', 'shift',
            'unshift']
