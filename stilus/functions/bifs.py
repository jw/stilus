from stilus.functions import addProperty, adjust, alpha, baseConvert, \
    basename, blend, blue, clone, contrast, convert, currentMedia, define, \
    dirname, error, extname, green, hsl, hsla, hue, imageSize, json, \
    length, lightness, listSeparator, lookup, luminosity, math, math_prop, \
    operate, p, pathjoin, pop, push, range, red, remove, replace, rgb, \
    rgba, s, saturation, shift, tan, trace, type_function, unit, unquote, \
    unshift, warn, prefixClasses, selectorExists, selector, stilus_slice, \
    stilus_split, substr

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
    'operate': operate.operate,
    'p': p.p,
    'pathjoin': pathjoin.pathjoin,
    'pop': pop.pop,
    '-prefix-classes': prefixClasses.prefix_classes,
    'push': push.push,
    'prepend': unshift.unshift,
    'range': range.range_function,
    'red': red.red,
    'remove': remove.remove,
    'replace': replace.replace,
    'rgb': rgb.rgb,
    'rgba': rgba.rgba,
    's': s.s,
    'saturation': saturation.saturation,
    'selector': selector.selector,
    'selector-exists': selectorExists.selector_exists,
    'shift': shift.shift,
    'slice': stilus_slice.slice,
    'split': stilus_split.split,
    'substr': substr.substr,
    'tan': tan.tan,
    'trace': trace.trace,
    'type': type_function.type_function,
    'typeof': type_function.type_function,
    'unit': unit.unit,
    'unquote': unquote.unquote,
    'unshift': unshift.unshift,
    'warn': warn.warn,
}

raw_bifs = ['add_property', 'append', 'base_convert', 'clone',
            'length', 'list_separator', 'p', 'pop', 'push',
            'prepend', 's', 'selector', 'shift', 'slice', 'unshift']
