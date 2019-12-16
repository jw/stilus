from functions import addProperty, adjust, alpha, baseConvert, basename, \
    blend, blue, clone, contrast, convert, currentMedia, define, dirname, \
    error, extname, green, hsl, hsla, hue, imageSize, json, length, \
    lightness, listSeparator, lookup, luminosity, match, math, math_prop, \
    merge, operate, oppositePosition, p, pathjoin, pop, prefixClasses, push, \
    range, red, remove, replace, rgb, rgba, s, saturation, \
    selector, selectorExists, selectors, shift, stilus_slice, stilus_split, \
    substr, tan, trace, transparentify, type_function, unit, unquote, \
    unshift, url, warn

bifs = {
    '-math-prop': math_prop.math_prop,
    'add-property-function': addProperty.add_property,
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
    'embedurl': url.url,
    'error': error.error,
    'extend': merge.merge,
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
    'match': match.match,
    'math': math.math,
    'merge': merge.merge,
    'operate': operate.operate,
    'opposite-position': oppositePosition.opposite_position,
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
    'selectors': selectors.selectors,
    'shift': shift.shift,
    'slice': stilus_slice.slice,
    'split': stilus_split.split,
    'substr': substr.substr,
    'tan': tan.tan,
    'trace': trace.trace,
    'transparentify': transparentify.transparentify,
    'type': type_function.type_function,
    'typeof': type_function.type_function,
    'unit': unit.unit,
    'unquote': unquote.unquote,
    'unshift': unshift.unshift,
    # 'url': url.url,
    'warn': warn.warn,
}

raw_bifs = ['add_property', 'append', 'base_convert', 'clone', 'embedurl',
            'extend', 'length', 'list_separator', 'merge',
            'opposite_position', 'p', 'pop', 'push', 'prepend',
            's', 'selector', 'shift', 'slice', 'unshift']
